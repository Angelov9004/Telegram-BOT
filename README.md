# SysBot – Telegram System Admin Bot

SysBot is a secure Telegram bot for **remote system monitoring and administration** of Linux servers.  
It allows a single authorized user to:

-  Authenticate securely for a limited time
- View live system status (CPU, RAM, disk, temperatures)
-  Reboot the server
-  Shut down the server
-  Execute shell commands with logging
-  Receive automatic alerts on high resource usage

---

## Project Structure


TELEGRAM-BOT/
├── sysbot.py
├── .env
├── requirements.txt
├── .gitignore
└── README.md



## Quick Start

    sudo apt install -y python3 python3-pip python3-venv lm-sensors
    python3 -m venv venv
    source venv/bin/activate
    pip install python-telegram-bot python-dotenv psutil


## Clone the Repository

    git clone git@github.com:Angelov9004/Telegram-BOT.git
    cd Telegram-BOT


## Create and Activate a Virtual Environment

     python3 -m venv .venv
     source .venv/bin/activate


## Install Dependencies

    pip install -r requirements.txt


## Create a .env File

    nano .env  / or sudo nano .env


## Add the following content:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AUTHORIZED_USER_ID=your_telegram_user_id
AUTH_PASSWORD=your_secret_password

 You can get your bot token from @BotFather
 To get your Telegram user ID, send /start to @userinfobot


### Features

/auth <password>

Authenticates you for 30 minutes.
/status

Returns current system health:

   CPU usage

   RAM usage

   Disk usage

   Temperatures (if lm-sensors is installed)

/reboot and /shutdown

Reboots or powers off the server.
/start

Shows interactive buttons (status, reboot, shutdown).


## Shell Commands

Once authenticated, you can send any shell command (e.g., uptime, ls, df -h) and the output will be sent back to the chat.
Auto Alerts

Every 5 minutes, the bot checks:

   CPU usage > 90%

   RAM usage > 90%

   Disk usage > 90%

If any threshold is exceeded, it notifies the authorized user.
   Security

   Only one authorized user (defined in .env) can use the bot.

   Output is limited to 4000 characters per message.

   All shell commands are logged to /var/log/telegram_bot.log.


## Requirements


   Linux-based system

   Python 3.8+

   (Optional) Temperature support:

    sudo apt install lm-sensors
    sudo sensors-detect

   Choose YES to all ,  Y !


## Create a systemd Service

    sudo nano /etc/systemd/system/sysbot.service


   Paste inside this : 

     [Unit]
     Description=SysBot Telegram Bot
     After=network-online.target
     Wants=network-online.target
     
     [Service]
     WorkingDirectory=/path/to/sysbot
     ExecStart=/path/to/sysbot/.venv/bin/python sysbot.py
     Restart=always
     User=your_user
     EnvironmentFile=/path/to/sysbot/.env
     
     [Install]
     WantedBy=multi-user.target



## AFTER: 

 
    sudo systemctl daemon-reload
    sudo systemctl enable sysbot
    sudo systemctl start sysbot
    sudo systemctl status sysbot

   
ENJOY !  
    




