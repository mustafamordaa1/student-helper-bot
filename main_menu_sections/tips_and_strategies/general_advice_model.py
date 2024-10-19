"""
Represents the general advice data model.

This class provides methods to interact with the general advice data stored in an Excel file, such as:
- Getting a list of available advice sheets.
- Retrieving questions from a specific advice sheet.
- Getting the answer to a specific question.
"""
from .excel_handler import ExcelHandler


class GeneralAdviceModel:
    def __init__(self, excel_handler: ExcelHandler):
        self.excel_handler = excel_handler

    def get_sheet_names(self) -> list:
        return self.excel_handler.get_sheet_names()

    def get_sheet_questions(self, sheet_name: str) -> list:
        data = self.excel_handler.get_sheet_data(sheet_name)
        return [row[0] for row in data]

    def get_answer(self, sheet_name: str, question_index: int) -> str:
        return self.excel_handler.get_cell_value(sheet_name, question_index + 2, 2)
