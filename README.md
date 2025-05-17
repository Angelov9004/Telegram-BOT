# SysBot – Telegram System Admin Bot

SysBot is a secure Telegram bot for **remote system monitoring and administration** of Linux servers. It allows a single authorized user to:

- Authenticate securely for a limited time
-  View live system status (CPU, RAM, disk, temperatures)
-  Reboot the server
-  Shut down the server
- Execute shell commands with logging
- ⚠ Receive automatic alerts on high resource usage

---

##  Project Structure

sysbot/
├── sysbot.py
├── .env
├── requirements.txt
├── .gitignore
└── README.md


---

##  Quick Start

### 1. Clone the repository

git clone https://github.com/your-username/sysbot.git
cd sysbot

2. Create and activate a virtual environment

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Create a .env file in the root folder:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AUTHORIZED_USER_ID=your_telegram_user_id
AUTH_PASSWORD=your_secret_password

     You can get TELEGRAM_BOT_TOKEN from @BotFather
     To get your Telegram user ID, send /start to @userinfobot

 Features
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
 Shell Commands

Once authenticated, you can send any shell command (e.g., uptime, ls, df -h) and the output will be sent back to the chat.
 Auto Alerts

Every 5 minutes, the bot checks:

    CPU usage > 90%

    RAM usage > 90%

    Disk usage > 90%

If any threshold is exceeded, it notifies the authorized user.
 Security

    Only one authorized user (from .env) can use the bot.

    Command output is limited to 4000 characters.

    All shell commands are logged to /var/log/telegram_bot.log.

 Requirements

    Linux-based system

    Python 3.8+

    lm-sensors (optional for temperature readings):

sudo apt install lm-sensors
sudo sensors-detect

 Create a systemd Service

sudo nano /etc/systemd/system/sysbot.service

Paste this content:

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

 Save and exit:

    CTRL + O, then Enter to save

    CTRL + X to exit

 Reload and enable on startup:

sudo systemctl daemon-reload
sudo systemctl enable sysbot
sudo systemctl start sysbot

 License

MIT – free to use and modify.

