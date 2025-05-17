import os
import asyncio
import subprocess
from dotenv import load_dotenv
from datetime import datetime, timedelta
import psutil

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, CallbackQueryHandler
)

load_dotenv()

class SysBot:
    def __init__(self):
        self.TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.AUTHORIZED_USER = int(os.getenv("AUTHORIZED_USER_ID"))
        self.AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "defaultPassword")
        self.SESSION_DURATION = timedelta(minutes=30)
        self.user_sessions = {}
        self.LOG_FILE = "/var/log/telegram_bot.log"

        self.app = ApplicationBuilder().token(self.TOKEN).build()

        self.app.add_handler(CommandHandler("auth", self.auth))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("reboot", self.reboot))
        self.app.add_handler(CommandHandler("shutdown", self.shutdown))
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))

    def log_command(self, user_id, cmd):
        with open(self.LOG_FILE, "a") as f:
            f.write(f"{datetime.now()} - User {user_id} ran: {cmd}\n")

    def is_authenticated(self, user_id):
        return user_id in self.user_sessions and self.user_sessions[user_id] > datetime.now()

    async def auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.AUTHORIZED_USER:
            return
        if not context.args:
            return

        if context.args[0] == self.AUTH_PASSWORD:
            self.user_sessions[update.effective_user.id] = datetime.now() + self.SESSION_DURATION
            await update.message.reply_text(" Authentication successful. You have access for 30 minutes.")

    async def shutdown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.AUTHORIZED_USER:
            return
        if not self.is_authenticated(update.effective_user.id):
            return
        await update.message.reply_text(" Shutting down...")
        os.system("sudo /sbin/shutdown -h now")

    async def reboot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.AUTHORIZED_USER:
            return
        if not self.is_authenticated(update.effective_user.id):
            return
        await update.message.reply_text(" Rebooting...")
        os.system("sudo /sbin/reboot")

    def get_system_status(self):
        try:
            temps_output = subprocess.check_output(["sensors"], text=True)
        except Exception:
            temps_output = " Could not retrieve temperatures (lm-sensors needed)."

        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return (
            f" Temperatures:\n{temps_output.strip()}\n\n"
            f" CPU usage: {cpu_percent}%\n"
            f" RAM: {ram.used // (1024 ** 2)}MB / {ram.total // (1024 ** 2)}MB ({ram.percent}%)\n"
            f" Disk: {disk.used // (1024 ** 3)}GB / {disk.total // (1024 ** 3)}GB ({disk.percent}%)"
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.AUTHORIZED_USER:
            return
        if not self.is_authenticated(update.effective_user.id):
            return
        await update.message.reply_text(" Gathering system information...")
        report = self.get_system_status()
        if len(report) > 4000:
            report = report[:4000] + "\n... (truncated)"
        await update.message.reply_text(report)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.AUTHORIZED_USER:
            return
        if not self.is_authenticated(update.effective_user.id):
            return

        keyboard = [
            [InlineKeyboardButton(" Status", callback_data="status")],
            [InlineKeyboardButton(" Reboot", callback_data="reboot")],
            [InlineKeyboardButton(" Shutdown", callback_data="shutdown")],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose an action:", reply_markup=markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query.from_user.id != self.AUTHORIZED_USER:
            return
        if not self.is_authenticated(query.from_user.id):
            return
        await query.answer()

        if query.data == "status":
            await self.status(update, context)
        elif query.data == "reboot":
            await self.reboot(update, context)
        elif query.data == "shutdown":
            await self.shutdown(update, context)

    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != self.AUTHORIZED_USER:
            return
        if not self.is_authenticated(update.effective_user.id):
            return

        text = update.message.text.strip()
        if not text:
            return

        try:
            self.log_command(update.effective_user.id, text)
            output = subprocess.check_output(text, stderr=subprocess.STDOUT, shell=True, timeout=10, text=True)
        except subprocess.CalledProcessError as e:
            output = f" Error:\n{e.output}"
        except Exception as e:
            output = f" Exception: {str(e)}"

        if len(output) > 4000:
            output = output[:4000] + "\n... (truncated)"

        await update.message.reply_text(f" Result:\n{output}")

    async def periodic_check(self):
        while True:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            alerts = []

            if cpu > 90:
                alerts.append(f" CPU usage: {cpu}%")
            if ram.percent > 90:
                alerts.append(f" RAM usage: {ram.percent}%")
            if disk.percent > 90:
                alerts.append(f" Disk almost full: {disk.percent}%")

            if alerts:
                await self.app.bot.send_message(chat_id=self.AUTHORIZED_USER, text="\n".join(alerts))

            await asyncio.sleep(300)

    def run(self):
        self.app.job_queue.run_once(lambda _: asyncio.create_task(self.periodic_check()), 1)
        print(" Bot started.")
        self.app.run_polling()


if __name__ == "__main__":
    bot = SysBot()
    bot.run()
