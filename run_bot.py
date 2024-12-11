import os
import re
import hikari
import asyncio
from pathlib import Path

# --------------------- FILL IN THESE FIELDS ---------------------- #
bot = hikari.GatewayBot("YOUR-BOT-TOKEN-HERE") # You need to create a discord bot and copy the token ( https://discord.com/developers/applications )
user_id = 12345678987654321 # Replace with your Discord User ID ( https://www.youtube.com/watch?v=SNxNNpiRR1M )
MACHINE_NAME = "MachineName" # Replace with your machine name (keep it reasonable, you'll need it later for the ?status command)
# ----------------------------------------------------------------- #

# Setup
CHOPPING_REGEX = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2}) \[INF\] Connection id ".*?", Request id ".*?": the application completed without reading the entire request body\.' 
DEGRADED_REGEX = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2}) \[WRN\] Node Compatibility Workload Failure (.*?) NodeCompatibilityMessage {(.*?)}'
CHOPPING_STATE_REGEX = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2}) \[INF\] Running State: (\w+)'
BALANCE_REGEX = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2}) \[INF\] Wallet: Current\(([\d.]+)\), Predicted\(([-\d.]+)\)'
log_dir = Path("C:/ProgramData/Salad/logs")


# Cache
processed_matches = set()

async def send_dm(user_id: int, content: str):
    try:
        user = await bot.rest.fetch_user(user_id)
        await user.send(content)
    except Exception as e:
        print(f"Failed to send DM to {user_id}: {e}")

async def check_logs():
    log_files = sorted(log_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)[:1]

    if not log_files:
        print("No log files found!")
        return

    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()

                chopping_match = re.search(CHOPPING_REGEX, content)
                if chopping_match:
                    timestamp = chopping_match.group(1)
                    most_recent_chopping = (
                        f"# Chopping Indefinitely\n\n"
                        f"- **Timestamp**: `{timestamp}`\n"
                        f"- **Machine Name**: `{MACHINE_NAME}`\n"
                        f"- **Status**: `Chopping Indefinitely`"
                    )
                    if most_recent_chopping not in processed_matches:
                        processed_matches.add(most_recent_chopping)
                        await send_dm(user_id, most_recent_chopping)

                degraded_match = re.search(DEGRADED_REGEX, content, re.DOTALL)
                if degraded_match:
                    timestamp, _, details = degraded_match.groups()
                    detail_parts = dict(part.split(" = ", 1) for part in details.split(", "))
                    title = detail_parts.get("Title", "Unknown")
                    body = detail_parts.get("Body", "No description provided.")
                    exit_code = detail_parts.get("ExitCode", "Unknown")
                    help_link_title = detail_parts.get("HelpLinkTitle", "Unknown")
                    help_link_action = detail_parts.get("HelpLinkAction", "Unknown")

                    most_recent_degraded = (
                        f"# Degraded\n\n"
                        f"- **Timestamp**: `{timestamp}`\n"
                        f"- **Machine Name**: `{MACHINE_NAME}`\n"
                        f"- **Details**:\n"
                        f"  - **Title**: `{title}`\n"
                        f"  - **Body**: `{body}`\n"
                        f"  - **Exit Code**: `{exit_code}`\n"
                        f"  - **Help Link**: [{help_link_title}]({help_link_action})"
                    )
                    if most_recent_degraded not in processed_matches:
                        processed_matches.add(most_recent_degraded)
                        await send_dm(user_id, most_recent_degraded)
                

        except Exception as e:
            print(f"Error reading file {log_file}: {e}")


async def get_status(truncate):
    log_files = sorted(log_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)[:1]

    if not log_files:
        return "No log files found!"

    most_recent_running_state = None
    most_recent_wallet = None

    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()

                running_match = re.findall(CHOPPING_STATE_REGEX, content)
                if running_match:
                    timestamp, state = running_match[-1]  # Get the latest match

                    # Make response more user readable
                    if state == "true":
                        state = "Chopping"
                    elif state == "false":
                        state = "Not Chopping"

                    if not truncate:
                        most_recent_running_state = (
                            f"# Running State\n\n"
                            f"- **Machine Name**: `{MACHINE_NAME}`\n"
                            f"- **Timestamp**: `{timestamp}`\n"
                            f"- **State**: `{state}`"
                        )

                    elif truncate:
                        most_recent_running_state = (
                        f"**Machine Name**: `{MACHINE_NAME}` "
                        f"**Timestamp**: `{timestamp}` "
                        f"**State**: `{state}`"
                    )

                wallet_match = re.findall(BALANCE_REGEX, content)
                if wallet_match:
                    timestamp, current_balance, predicted_balance = wallet_match[-1]  # Get the latest match

                    if not truncate:
                        most_recent_wallet = (
                            f"# Wallet Balance\n\n"
                            f"- **Machine Name**: `{MACHINE_NAME}`\n"
                            f"- **Timestamp**: `{timestamp}`\n"
                            f"- **Current Balance**: `{current_balance}`\n"
                            f"- **Predicted Balance**: `{predicted_balance}`"
                        )

                    elif truncate:
                        timestamp, current_balance, predicted_balance = wallet_match[-1]
                        most_recent_wallet = (
                            f""
                        )
        except Exception as e:
            print(f"Error reading file {log_file}: {e}")

    status_message = []
    if most_recent_running_state:
        status_message.append(most_recent_running_state)
    if most_recent_wallet:
        status_message.append(most_recent_wallet)

    return "\n\n".join(status_message) if status_message else "No relevant entries found in logs."

# Event Listeners
@bot.listen(hikari.StartedEvent)
async def on_started(event):
    print("Bot started!")
    asyncio.create_task(periodic_check())

@bot.listen(hikari.MessageCreateEvent)
async def on_message(event):
    if event.is_bot or not event.content:
        return

    content = event.content.strip().lower()
    if content.startswith("?status"):
        try:
            parts = content.split(maxsplit=1)
            machine_name = parts[1] if len(parts) > 1 else "Unknown Machine"
            if machine_name.lower() == MACHINE_NAME.lower():
                status = await get_status(False)
                await event.message.respond(status)
            elif machine_name.lower() == "all":
                status = await get_status(True)
                await event.message.respond(status)                
            
        except IndexError:
            await event.message.respond("Please provide a machine name, e.g., `?status MachineName`.")

    # if content.startswith("?help"):
        # try:
            # await event.message.respond("**?status MachineName** -- shows status for that machine\n**?machines** -- shows list of machines")
        # except:
            # print("error sending help command??? how tf")

    if content.startswith("?machines"):
        try:
            await event.message.respond(MACHINE_NAME)                
        except IndexError:
            await event.message.respond("Something went wrong... is the MACHINE_NAME missing?")

async def periodic_check():
    while True:
        await check_logs()
        await asyncio.sleep(15)  # Sleep for 15 seconds

@bot.listen(hikari.StartedEvent)
async def on_started(event):
    print("Bot started!")
    asyncio.create_task(periodic_check())

bot.run()
