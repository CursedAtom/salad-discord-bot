# salad-discord-bot
### Discord bot to help you monitor your machines on Salad


## How to use:
### 1. Install dependencies (this needs to be done on every machine you plan to monitor):
```cmd
pip install hikari
```
### 2. Create a Discord Bot and make sure to note down the token. You will need it later.
- Add the Discord Bot to a server you're in (this lets the bot send you a DM)
- This video will showcase how you make a bot and add it to a server. You should just give it the "Bot" scope and ignore the permissions, they're not necessary for this project.<br>
[![image](https://img.youtube.com/vi/4XswiJ1iUaw/0.jpg)](https://www.youtube.com/embed/4XswiJ1iUaw?start=0&end=115)

### 3. Fill in lines 8-10
![image](https://github.com/user-attachments/assets/8f987d3c-d932-4d08-8a8f-44caf51cfda0)
- Add your Discord Bot Token. 
- Add your Discord User ID.<br>
[![image](https://img.youtube.com/vi/SNxNNpiRR1M/0.jpg)](https://www.youtube.com/watch?v=SNxNNpiRR1M)
- Add a name for the machine (this needs to be unique if you plan to use this on multiple machines). Keep it reasonable, you'll need it later for the ?status command

### 4. Run the script on each machine you wish to monitor, making sure to change the Machine Name for each
```cmd
python.exe run_bot.py
```


### Commands:
- ?machines -- Lists every machine that is currently being monitored. It sends a message for each machine, so it may get a bit spammy if you have a lot of machines
- ?status MachineName -- Lists the status of the machine named
- ?status all -- Lists the statuses of every machine in a truncated format
#### I had a ?help command but it would get spammy because every machine would respond. It's currently commented out, but you can uncomment it on one of the machines if you wish to have a ?help command.
