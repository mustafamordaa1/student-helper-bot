import pandas as pd

from config import FAQ_FILE


# Load the Excel file
try:
    df = pd.read_excel(FAQ_FILE)
except FileNotFoundError:
    print("Excel file not found. Make sure it's in the correct directory.")
    exit()


async def get_faq_categories():
    """Gets unique FAQ categories from the Excel file."""
    return df["category"].unique().tolist()


def get_category_name_by_index(index: int):
    """Retrieves the category name from the DataFrame using its index."""
    try:
        return df["category"].iloc[index]
    except IndexError:
        print(f"Invalid category index: {index}")
        return None


async def get_faqs_by_category(category):
    """Gets FAQs for a specific category from the Excel file."""
    category_faqs = df[df["category"] == category]
    return zip(category_faqs["question"], category_faqs["answer"], category_faqs.index)


async def get_faq_by_id(question_id):
    """Gets a specific FAQ by its ID (row index in the DataFrame)."""
    question = df.loc[question_id, "question"]
    answer = df.loc[question_id, "answer"]
    return question, answer
