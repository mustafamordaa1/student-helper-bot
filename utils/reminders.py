import datetime
import pandas as pd
from telegram import Bot, Update
from telegram.ext import Application, CallbackContext, CommandHandler

from config import REMINDER_FILE
from utils import user_management
from apscheduler.schedulers.asyncio import AsyncIOScheduler



async def send_reminder(bot: Bot, user_id: int, reminder_text: str, use_tts: bool):
    """Sends a reminder to the user."""

    await bot.send_message(user_id, text=reminder_text)
    # if use_tts:
    #     audio_file_path = await generate_tts(reminder_text)
    #     await bot.send_voice(user_id, voice=open(audio_file_path, 'rb'))
    #     os.remove(audio_file_path)
    # else:
    #     await bot.send_message(user_id, text=reminder_text)


async def schedule_reminders(bot: Bot):
    """Schedules reminders for all users based on their preferences."""
    users = await user_management.get_all_users_with_reminders()
    reminders_df = pd.read_excel(REMINDER_FILE)
    
    # Get the first column (assuming it's named 'Reminder')
    # reminders = reminders_df['Reminder'].tolist() 
    for user in users:
        # user_id = user["telegram_id"]
        # frequency = user["reminder_times_per_week"]
        # preferred_method = user["voice_written"]  # Assuming "صوت" or "نص"
        print(user)
        user_id = int(user[0])
        user_name = user[1]
        frequency = user[2]
        preferred_method = user[3]
        use_tts = preferred_method == "صوت"

        # Determine reminder days (e.g., spread evenly throughout the week)
        reminder_days = [
            datetime.datetime.today().weekday() + i for i in range(frequency)
        ]
        reminder_days = [
            day % 7 for day in reminder_days
        ]  # Ensure days are within 0-6 (Mon-Sun)

        for day in reminder_days:
            # Schedule a reminder for each day at a specific time (e.g., 10:00 AM)
            reminder_time = datetime.time(10, 0)  # You can adjust the time
            reminder_datetime = datetime.datetime.combine(
                datetime.datetime.today()
                + datetime.timedelta(
                    days=(day - datetime.datetime.today().weekday()) % 7
                ),
                reminder_time,
            )
            # Choose a random reminder from the Excel file
            # reminder_text = reminders_df.sample(n=1)["Reminder"].values[0]
            
            # Choose a random reminder from the first column (index 0)
            reminder_text = reminders_df.iloc[:, 0].sample(n=1).values[0] 
            reminder_text = reminder_text.replace(
                "(اسم المستخدم)", user_name
            )

            # scheduler.add_job(
            #     send_reminder,
            #     "cron",
            #     day_of_week=day,
            #     hour=reminder_time.hour,
            #     minute=reminder_time.minute,
            #     args=[bot, user_id, reminder_text, use_tts],
            # )
            
            run_date = datetime.datetime.now() + datetime.timedelta(seconds=10) # Run in 10 seconds
            scheduler.add_job(send_reminder, 'date', run_date=run_date, args=[bot, user_id, reminder_text, use_tts])


async def test_reminders(update: Update, context: CallbackContext):
    """Test command to send a reminder immediately."""
    user_id = update.effective_user.id  # Or use a specific test user ID
    reminder_text = "This is a test reminder!"
    use_tts = True  # Or False, depending on your test case

    await send_reminder(context.bot, user_id, reminder_text, use_tts)


def register_reminders_handlers(application: Application):

    # Initialize and start the scheduler
    global scheduler  # Make scheduler accessible within the main function
    scheduler = AsyncIOScheduler()
    # scheduler.add_job(
    #     schedule_reminders, "cron", day="*", hour=0, minute=0, args=[application.bot]
    # )  # Schedule daily at midnight
    # scheduler.add_job(schedule_reminders, 'cron', minute='*', args=[application.bot]) # Run every minute for testing
    scheduler.start()

    # Add a test command to trigger a reminder immediately
    application.add_handler(CommandHandler("test_reminder", test_reminders))
