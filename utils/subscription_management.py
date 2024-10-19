from datetime import datetime, timedelta
import openpyxl
import random
import string

from telegram import Update

from utils import database



async def handle_subscription_purchase(user_id, plan_details):
    """Handles the purchase of a subscription plan (replace with your payment processing logic)."""
    # ... (Your payment processing logic here)

    # After successful payment, update the user's subscription details in the SQLite database:
    database.execute_query(
        "UPDATE users SET type_of_last_subscription = ?, subscription_end_time = ? WHERE telegram_id = ?",
        (plan_details["subscription_type"], plan_details["subscription_end_date"], user_id),
    )
    return True

async def get_subscription_details(user_id):
    """Retrieves the "Type of Last Subscription" and "Subscription End Date" 
       from the SQLite database for a given user_id."""
    subscription_details = database.get_data("SELECT type_of_last_subscription, subscription_end_time FROM users WHERE telegram_id = ?", (user_id,))
    return subscription_details[0] if subscription_details else (None, None)

async def activate_free_trial(user_id):
    """Activates a free trial for a user if eligible."""
    subscription_type, subscription_end_date = await get_subscription_details(user_id)

    if subscription_type:
        database.execute_query(
            "UPDATE users SET type_of_last_subscription = ?, subscription_end_time = ? WHERE telegram_id = ?",
            (
                "تجربة مجانية",
                (datetime.now() + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
                user_id,
            ),
        )
        return True  # Trial activated successfully
    return False  # Not eligible for free trial


async def handle_referral(user_id, referral_code):
    """Handles referrals, extending subscriptions for both the referred user and the referrer."""
    referrer_id = database.get_data(
        "SELECT telegram_id FROM users WHERE referral_code = ?", (referral_code,)
    )

    if referrer_id:  # Referral code is valid
        referrer_id = referrer_id[0][0]  # Extract the telegram_id from the result

        # Update referred user's subscription
        database.execute_query(
            "UPDATE users SET subscription_end_time = CASE WHEN subscription_end_time IS NOT NULL THEN strftime('%Y-%m-%d %H:%M:%S', datetime(subscription_end_time, '+3 days')) ELSE NULL END WHERE telegram_id = ?",
            (user_id,),
        )

        # Update referrer's subscription
        database.execute_query(
            "UPDATE users SET subscription_end_time = CASE WHEN subscription_end_time IS NOT NULL THEN strftime('%Y-%m-%d %H:%M:%S', datetime(subscription_end_time, '+3 days')) ELSE NULL END, number_of_referrals = number_of_referrals + 1 WHERE telegram_id = ?",
            (referrer_id,), 
        )
        return True
    return False

# Function to check subscription status, can be reused in all handlers
async def check_subscription(update: Update, context):
    """Checks if the user has an active subscription and handles the response."""
    if isinstance(update, Update):
        query = update.message
    else:
        query = update.callback_query
        await query.answer()
    user_id = update.effective_user.id

    subscription_data = database.get_data(
        "SELECT subscription_end_time FROM users WHERE telegram_id = ?", (user_id,)
    )

    if subscription_data and subscription_data[0][0] is not None:
        subscription_end_time = datetime.strptime(subscription_data[0][0], "%Y-%m-%d %H:%M:%S")
        if subscription_end_time > datetime.now():
            return True  # Subscription is active
        else:
            if isinstance(update, Update):
                await query.reply_text("انتهت صلاحية اشتراكك. يرجى الاشتراك للوصول إلى هذا القسم.")
            else:
                await query.edit_message_text("انتهت صلاحية اشتراكك. يرجى الاشتراك للوصول إلى هذا القسم.")
            return False  # Subscription has expired
    else:
        if isinstance(update, Update):
            await query.reply_text("أنت لا تمتلك اشتراكًا. اشترك الآن للاستمتاع بميزات إضافية!")
        else:
            await query.edit_message_text("أنت لا تمتلك اشتراكًا. اشترك الآن للاستمتاع بميزات إضافية!")
        return False  # No subscription found


SERIAL_CODE_DATA = {
    "ABC": {"duration_months": 1, "filename": "serial_codes/serial_codes_1month.xlsx"},
    "DEF": {"duration_months": 3, "filename": "serial_codes/serial_codes_3months.xlsx"},
    "GHI": {"duration_months": 12, "filename": "serial_codes/serial_codes_1year.xlsx"},
}


def generate_serial_codes(num_codes, code_prefix, file_name):
    """Generates unique serial codes and stores them in an Excel file."""
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.append(["Serial Code"])  # Add header row

    generated_codes = set()  # Use a set to ensure uniqueness

    while len(generated_codes) < num_codes:
        code = code_prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=9))
        if code not in generated_codes:
            generated_codes.add(code)
            worksheet.append([code])

    workbook.save(file_name)
    print(f"{num_codes} serial codes generated and saved to {file_name}")

def create_serial_code_files(serial_code_data=SERIAL_CODE_DATA):
    """Creates Excel files for serial codes based on provided data."""
    for code_prefix, data in serial_code_data.items():
        generate_serial_codes(100, code_prefix, data["filename"])  # Generate 100 codes per type