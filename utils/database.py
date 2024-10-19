import sqlite3

from telegram import Update
from telegram.ext import CallbackContext
from config import DATABASE_FILE
from utils.question_management import (
    generate_questions_with_categories,
    generate_verbal_questions,
)


def create_connection():
    """Creates a connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


async def create_tables(update: Update, context: CallbackContext):
    """Creates all the necessary tables in the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Users Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT,
            name TEXT,
            class TEXT,
            voice_written TEXT,
            taking_qiyas_before TEXT,
            last_score INTEGER DEFAULT 0,
            referral_code TEXT,
            gender TEXT,
            subscription_end_time TEXT,
            type_of_last_subscription TEXT,
            reminder_times_per_week INTEGER DEFAULT 0,
            percentage_expected INTEGER DEFAULT 0,
            usage_time TEXT,
            number_of_daily_gifts_used INTEGER DEFAULT 0,
            last_daily_reward_claim TEXT,
            total_number_of_created_questions INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            person_referred_me TEXT,
            number_of_referrals INTEGER,
            telegram_username TEXT,
            telegram_id INTEGER,
            personal_photo_link TEXT,
            telegram_bio TEXT,
            notifications_enabled BOOLEAN DEFAULT FALSE
        )
    """
    )

    # ai_image_usage Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_image_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            usage_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """
    )

    # FAQs Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """
    )

    # Categorys Tables
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS main_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL 
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subcategories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS main_sub_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_category_id INTEGER,
            subcategory_id INTEGER,
            FOREIGN KEY (main_category_id) REFERENCES main_categories(id) ON DELETE CASCADE,
            FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE CASCADE,
            UNIQUE(main_category_id, subcategory_id) 
        )
    """
    )

    # Questions Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correct_answer TEXT,
            question_text TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            explanation TEXT,
            main_category_id INTEGER, 
            question_type TEXT DEFAULT 'quantitative', 
            image_path TEXT,
            FOREIGN KEY (main_category_id) REFERENCES main_categories(id) ON DELETE CASCADE
        )
    """
    )

    # Level Determinations table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS level_determinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            num_questions INTEGER,
            percentage REAL,
            time_taken REAL,
            pdf_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )

    # Level Determination Answers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS level_determination_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            user_answer TEXT,
            is_correct INTEGER,
            level_determination_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
            FOREIGN KEY (level_determination_id) REFERENCES level_determinations(id) ON DELETE CASCADE
        )
    """
    )

    # User Answers Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            previous_tests_id INTEGER,
            question_id INTEGER,
            user_answer TEXT,
            is_correct INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (previous_tests_id) REFERENCES previous_tests(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
    """
    )

    # Previous Tests Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS previous_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            num_questions INTEGER,
            score INTEGER,
            time_taken REAL,
            pdf_path TEXT,
            answers_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )

    # Chat History Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            messages TEXT
        )
    """
    )
    # await generate_questions_with_categories()
    generate_verbal_questions()
    conn.commit()
    conn.close()


def get_data(query, params=None):
    """Executes a SELECT query and returns the result."""
    conn = create_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data


def execute_query(query, params=None):
    """Executes a non-SELECT query (e.g., INSERT, UPDATE, DELETE)."""
    conn = create_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()
    conn.close()


def execute_query_return_id(query, params=None):
    """Executes a non-SELECT query and returns the last inserted row ID."""
    conn = create_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    lastrowid = cursor.lastrowid
    conn.commit()
    conn.close()
    return lastrowid