# MADevice

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

Provides a way to monitor devices being used in MAD without needing a browser. Get alerts in Discord when they have not updated for a set amount of time. As well as a way to get the status of your devices on demand without leaving Discord.
git 
## Requirements
* Python 3.7 (Only tested on 3.7, other Python 3 versions may work)


## Setup
* Clone this repo
* Run `pip[3[.7]] install -r requirements.txt`
* Ensure you have entered your server details and name into `servers.json` (take a copy from `server.json.example`)
    * This should be the IP and the port.
* Create `config.ini` from `config.ini.example` and populate the value which says `REQUIRED`


## Run

```
python[3[.7]] main.py
```


### No Data Alert
When running it will check the last received time for data and then if it is more than 20 minutes (or the values set in `alert_recheck_time`) in the past it will post a message to the channel set by `alert_channel_webhook`

![alert image](images/alert.png)

### On-Demand Status (`!status`)

If you type `!status` in the channel set by `alert_channel_id`  You get an on-demand update across all servers (set in servers.json) and posted into Discord rather than opening up multiple browsers to see the data.

![status image](images/status.png)



## FAQ

#### How to get `alert_channel_id`?

Enable developer mode -> https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-

Then go to the channel you want the messages to be posted in. Right-click and select `Copy ID` and paste in `config.ini`

#### How to create Discord token?

https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token

#### How do I add my Discord token to my server?

https://www.techjunkie.com/add-bots-discord-server/

