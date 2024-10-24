import datetime
import os
from typing import Dict
import pandas as pd
from telegram import Bot, Update
from telegram.ext import Application, CallbackContext, CommandHandler

from AIModels.tts import generate_tts
from config import REMINDER_FILE
from utils import user_management
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from apscheduler.triggers.interval import IntervalTrigger


class ReminderManager:
    def __init__(self, bot: Bot, reminder_file: str):
        self.bot = bot
        self.reminder_file = reminder_file
        self.scheduler = AsyncIOScheduler()
        self.user_jobs: Dict[int, list] = {}  # Store jobs by user_id
        self.reminders_df = pd.read_excel(reminder_file)

    async def send_reminder(self, user_id: int, user_name: str, use_tts: bool):
        """Sends a reminder to the user."""
        # Check if notifications are enabled for this user
        is_enabled = await user_management.get_user_setting(
            user_id, "notifications_enabled"
        )
        if not is_enabled:
            return

        reminder_text = self.reminders_df.iloc[:, 0].sample(n=1).values[0]
        reminder_text = reminder_text.replace("(اسم المستخدم)", user_name)

        if use_tts:
            audio_file_path = await generate_tts(reminder_text)
            await self.bot.send_voice(user_id, voice=open(audio_file_path, "rb"))
            os.remove(audio_file_path)
        else:
            await self.bot.send_message(user_id, text=reminder_text)

    def get_reminder_times(self, frequency: int) -> list:
        """Generate evenly distributed reminder times throughout the day."""
        if frequency <= 0:
            return []

        # Calculate the interval between reminders in minutes
        interval_minutes = (
            24 * 60
        ) // frequency  # Spread reminders evenly throughout the day
        base_time = datetime.datetime.now().replace(second=0, microsecond=0)

        # Generate reminder times
        reminder_times = [
            base_time + datetime.timedelta(minutes=i * interval_minutes)
            for i in range(frequency)
        ]

        return reminder_times

    def remove_user_jobs(self, user_id: int):
        """Remove all scheduled jobs for a user."""
        if user_id in self.user_jobs:
            for job in self.user_jobs[user_id]:
                self.scheduler.remove_job(job.id)
            self.user_jobs[user_id] = []

    async def schedule_user_reminders(
        self, user_id: int, user_name: str, frequency: int, preferred_method: str
    ):
        """Schedule or update reminders for a specific user (per day)."""
        # Remove existing jobs for this user
        self.remove_user_jobs(user_id)

        try:
            is_enabled = await user_management.get_user_setting(
                user_id, "notifications_enabled"
            )
            if not is_enabled or frequency <= 0:
                return
        except Exception as e:
            print(f"Error checking notification settings for user {user_id}: {e}")
            return

        use_tts = preferred_method == "voice"
        reminder_times = self.get_reminder_times(frequency)

        # Schedule new jobs
        new_jobs = []
        for reminder_time in reminder_times:
            logging.info(f"Scheduling reminder for user {user_id} at {reminder_time}")

            job = self.scheduler.add_job(
                self.send_reminder,
                "cron",  # Use 'cron' for recurring jobs
                hour=reminder_time.hour,  # Schedule for the calculated hour
                minute=reminder_time.minute,
                second=reminder_time.second,
                args=[user_id, user_name, use_tts],
                id=f"reminder_{user_id}_{reminder_time}",
            )
            new_jobs.append(job)

        self.user_jobs[user_id] = new_jobs

    async def initialize_all_reminders(self):
        """Initialize reminders for all users with active reminders."""
        users = await user_management.get_all_users_with_reminders()

        for user in users:
            user_id = int(user[0])
            user_name = user[1]
            frequency = user[2]
            preferred_method = user[3]

            await self.schedule_user_reminders(
                user_id, user_name, frequency, preferred_method
            )

    async def handle_notification_toggle(self, user_id: int, is_enabled: bool):
        """Handle notification toggle event."""
        if not is_enabled:
            # If notifications are disabled, remove all scheduled reminders
            self.remove_user_jobs(user_id)
        else:
            # If notifications are enabled, reschedule reminders
            try:
                user_name, preferred_method, frequency = (
                    await user_management.get_user_for_reminder(user_id)
                )

                await self.schedule_user_reminders(
                    user_id, user_name, frequency, preferred_method
                )
            except Exception as e:
                print(f"Error rescheduling reminders for user {user_id}: {e}")

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def get_jobs(self, application):
        for job in application.reminder_manager.scheduler.get_jobs():
            print(f"Job ID: {job.id}, Next Run Time: {job.next_run_time}")


async def register_reminders_handlers(application: Application):
    """Register reminder handlers and initialize the reminder manager."""
    reminder_manager = ReminderManager(application.bot, REMINDER_FILE)

    # Store the reminder manager in application context
    application.reminder_manager = reminder_manager

    # Initialize all reminders and start the scheduler
    await reminder_manager.initialize_all_reminders()
    reminder_manager.start()
    reminder_manager.get_jobs(application)


# async def adding_reminders(application: Application):

#     reminder_manager = ReminderManager(application.bot, REMINDER_FILE)
#     application.reminder_manager = reminder_manager  # Store reference in application

#     # Initialize all reminders
#     application.create_task(await reminder_manager.initialize_all_reminders())
#     reminder_manager.start()


# async def register_reminders_handlers(application: Application):
#     """Register reminder handlers and initialize the reminder manager."""
#     await adding_reminders(application)
