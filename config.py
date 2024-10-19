import os


API_PATH = "APIs"

# Bot token
BOT_TOKEN_PATH = os.path.join(API_PATH, "bot_token.txt")
BOT_TOKEN = open(BOT_TOKEN_PATH, "r").readline()

# OpenAI key
OPENAI_API_PATH = os.path.join(API_PATH, "openai.txt")
OPENAI_API_KEY = open(OPENAI_API_PATH, "r").readline()

# Main files directory
MAIN_FILES = "Main Files"

# Path to the folder containing welcoming materials
WELCOMING_FOLDER = "welcoming"

IMAGE_FOLDER = "Images"

# Path to your Database File
DATABASE_FILE = os.path.join(MAIN_FILES, "database.db")

# Excel files directory
EXCEL_FILES_DIRECTORY = os.path.join(MAIN_FILES, "Excel Files")

# Excel files
EXCEL_FILE_BASHAR = os.path.join(EXCEL_FILES_DIRECTORY, "الاسئلة الكمية.xlsx")
REMINDER_FILE = os.path.join(EXCEL_FILES_DIRECTORY, "reminders.xlsx")
VERBAL_FILE = os.path.join(EXCEL_FILES_DIRECTORY, "الاسئلة اللفظية.xlsx")
DESIGNS_FOR_MALE_FILE = os.path.join(EXCEL_FILES_DIRECTORY, "designs_for_male.xlsx")
DESIGNS_FOR_FEMALE_FILE = os.path.join(EXCEL_FILES_DIRECTORY, "designs_for_female.xlsx")


# Template files directory
TEMPLATE_FILES_DIRECTORY = os.path.join(MAIN_FILES, "Template Files")

# Word Files
WORD_FOLDER_PATH = os.path.join(TEMPLATE_FILES_DIRECTORY, "Word")
WORD_MAIN_PATH = os.path.join(WORD_FOLDER_PATH, "Main.docx")
Q_AND_A_FILE_PATH = os.path.join(WORD_FOLDER_PATH, "Q&A.docx")

# Power Point Files
POWERPOINT_FOLDER_PATH = os.path.join(TEMPLATE_FILES_DIRECTORY, "Powerpoint")
POWERPOINT_MAIN_PATH = os.path.join(POWERPOINT_FOLDER_PATH, "Main.pptx")
