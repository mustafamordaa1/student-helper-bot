from docxtpl import DocxTemplate
from docx2pdf import convert
from PyPDF2 import PdfMerger
import os
from datetime import datetime

from config import Q_AND_A_FILE_PATH
from utils import database


def generate_quiz_pdf(questions, user_id, category_name=None):
    """
    Generates a PDF quiz with the given questions using a Word template.
    Args:
        questions (list): A list of tuples, each containing question data.
    """
    # 1. Create the directory structure
    base_dir = "user_tests"
    user_dir = os.path.join(base_dir, str(user_id))
    os.makedirs(user_dir, exist_ok=True)  # Create if it doesn't exist

    # 2. Prepare the data for the Word template
    quiz_data = []
    for i, question_data in enumerate(questions):
        (
            question_id,
            correct_answer,
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            explanation,
            main_category_id,
            question_type,
            image_path,
        ) = question_data
        main_category_name = database.get_data(
            "SELECT name FROM main_categories WHERE id = ?", (main_category_id,)
        )

        quiz_data.append(
            {
                "QuestionNumber": i + 1,
                "QuestionText": question_text,
                "MainCategoryName": main_category_name[0][0],
                "OptionA": option_a,
                "OptionB": option_b,
                "OptionC": option_c,
                "OptionD": option_d,
                "CorrectAnswer": correct_answer,
                "Explanation": explanation,
            }
        )

    # 3. Generate the entire quiz Word document
    word_filename = os.path.join(
        user_dir, f"quiz_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
    )
    doc = DocxTemplate(Q_AND_A_FILE_PATH)
    doc.render({"questions": quiz_data})  # Pass the list of question data
    doc.save(word_filename)

    # 4. Convert the Word document to PDF
    pdf_filename = os.path.join(
        user_dir, f"quiz_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    )
    convert(word_filename, pdf_filename)

    # 5. Cleanup the temporary Word file
    if os.path.exists(word_filename):
        os.remove(word_filename)

    return pdf_filename


# def replace_placeholders_in_word(output_path, data):
#     """Replaces placeholders in the Word document."""
#     doc = DocxTemplate(Q_AND_A_FILE_PATH)
#     doc.render(data)
#     doc.save(output_path)


# def convert_docx_to_pdf(docx_path, pdf_path):
#     """Converts a .docx file to a .pdf file."""
#     convert(docx_path, pdf_path)


# def merge_pdfs(pdf_list, output_pdf):
#     """Merges multiple PDFs into a single PDF file."""
#     merger = PdfMerger()
#     for pdf in pdf_list:
#         merger.append(pdf)
#     merger.write(output_pdf)
#     merger.close()


# def cleanup_files(files):
#     """Deletes the specified files from the filesystem."""
#     for file in files:
#         if os.path.exists(file):
#             os.remove(file)

# def generate_quiz_pdf(questions, user_id, category_name=None):
#     """
#     Generates a PDF quiz with the given questions using a Word template.
#     Args:
#         questions (list): A list of tuples, each containing question data:
#                           (question_id, question_text, option_a, option_b,
#                            option_c, option_d, explanation (optional)).
#     """
#     # 1. Create the directory structure
#     base_dir = "user_tests"  # You can change this base directory if needed
#     user_dir = os.path.join(base_dir, str(user_id))
#     os.makedirs(user_dir, exist_ok=True)  # Create if it doesn't exist

#     # 2. Initialize variables to hold generated PDFs
#     pdf_list = []
#     temp_files = []

#     # 3. Loop through questions and generate individual PDFs
#     for i, question_data in enumerate(questions):
#         (
#             question_id,
#             correct_answer,
#             question_text,
#             option_a,
#             option_b,
#             option_c,
#             option_d,
#             explanation,
#             main_category_id,
#         ) = question_data
#         # main_category_name = database.get_data(
#         #     "SELECT name FROM main_categories WHERE id = ?", (main_category_id,)
#         # )

#         # Prepare the data for the Word template
#         data = {
#             "QuestionNumber": i + 1,
#             "QuestionText": question_text,
#             "MainCategoryName": category_name,
#             "OptionA": option_a,
#             "OptionB": option_b,
#             "OptionC": option_c,
#             "OptionD": option_d,
#             "CorrectAnswer": correct_answer,
#             "Explanation": explanation,
#         }

#         # Generate a temporary Word file for each question
#         word_filename = os.path.join(user_dir, f"question_{i + 1}.docx")
#         replace_placeholders_in_word(word_filename, data)
#         temp_files.append(word_filename)

#         # Convert the Word file to a PDF
#         pdf_filename = os.path.join(user_dir, f"question_{i + 1}.pdf")
#         convert_docx_to_pdf(word_filename, pdf_filename)

#         # Add the generated PDF to the list
#         pdf_list.append(pdf_filename)
#         temp_files.append(pdf_filename)

#     # 4. Merge all PDFs into one
#     merged_pdf_filename = os.path.join(
#         user_dir, f"quiz_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
#     )
#     merge_pdfs(pdf_list, merged_pdf_filename)

#     # 5. Cleanup temporary files
#     cleanup_files(temp_files)

#     return merged_pdf_filename  # Return the full path of the merged PDF


# from datetime import datetime
# import os
# import sqlite3
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch

# from config import DATABASE_FILE

# def generate_quiz_pdf(questions, main_category_id, user_id):
#     """Generates a PDF quiz with the given questions."""
#     # Fetch the main category name
#     conn = sqlite3.connect(DATABASE_FILE)
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM main_categories WHERE id = ?", (main_category_id,))
#     main_category_name = cursor.fetchone()[0]
#     conn.close()

#     # Create the directory structure
#     base_dir = "user_tests"
#     user_dir = os.path.join(base_dir, str(user_id))
#     os.makedirs(user_dir, exist_ok=True)

#     # Generate timestamped filename
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     test_number = len(os.listdir(user_dir)) + 1  # Get next test number
#     filename = f"{test_number}_{timestamp}.pdf"

#     filepath = os.path.join(user_dir, filename)
#     doc = SimpleDocTemplate(filepath, pagesize=letter)
#     styles = getSampleStyleSheet()
#     story = []

#     # Modify or create styles as needed
#     question_style = styles["Normal"]
#     question_style.fontSize = 12
#     question_style.spaceAfter = 10

#     option_style = styles["Normal"]
#     option_style.fontSize = 10
#     option_style.leftIndent = 20  # Indent options
#     option_style.spaceAfter = 5

#     # Add main category name to the first page
#     story.append(Paragraph(f"تصنيف: {main_category_name}", styles["Heading1"]))

#     for i, question_data in enumerate(questions):
#         question_id, correct_answer, question_text, option_a, option_b, option_c, option_d, *explanation = question_data

#         # Question Number and Text
#         question_num = i + 1
#         question_text = f"**{question_num}. {question_text}**"
#         story.append(Paragraph(question_text, question_style))

#         # Options
#         story.append(Paragraph(f"أ. {option_a}", option_style))
#         story.append(Paragraph(f"ب. {option_b}", option_style))
#         story.append(Paragraph(f"ج. {option_c}", option_style))
#         story.append(Paragraph(f"د. {option_d}", option_style))

#         # Add space for answer (or modify to create fillable forms)
#         story.append(Spacer(1, 0.5*inch))

#         # Optional: Add explanation (if provided)
#         if explanation:
#             explanation_text = explanation[0] # Assuming explanation is the 7th element in tuple
#             story.append(Paragraph(f"التوضيح: {explanation_text}", styles["Italic"]))
#             story.append(Spacer(1, 0.3*inch))

#         # Add page break after each question (or every few questions)
#         story.append(PageBreak())

#     doc.build(story)

#     return filepath
