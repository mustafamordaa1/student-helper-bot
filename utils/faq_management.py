from utils import database


async def get_faq_categories() -> list:
    """Retrieves distinct FAQ categories from the database."""
    categories = database.get_data("SELECT DISTINCT category FROM faqs")
    return [row[0] for row in categories]

async def get_faqs_by_category(category: str) -> list:
    """Retrieves FAQs for a specific category from the database."""
    faqs = database.get_data("SELECT question, answer, id FROM faqs WHERE category = ?", (category,))
    return faqs

async def get_faq_by_id(question_id: int) -> tuple:
    """Retrieves the question and answer for a given id."""
    result = database.get_data("SELECT question, answer FROM faqs WHERE id = ?", (question_id,))
    if result:
        return result[0]  # Returns a tuple (question, answer)
    else:
        return None, None  # Or handle the case where the question_id is not found