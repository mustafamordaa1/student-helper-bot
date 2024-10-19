"""
Represents the solution strategies data model.

This class provides methods to interact with the solution strategies data stored in an Excel file, such as:
- Getting a list of available solution strategies sheets.
- Retrieving questions from a specific solution strategies sheet.
- Getting the file path to the corresponding video, audio, text, or PDF for a specific question.
"""
from .excel_handler import ExcelHandler


class SolutionStrategiesModel:
    def __init__(self, excel_handler: ExcelHandler):
        self.excel_handler = excel_handler
        self.format_column_map = {"video": 2, "audio": 3, "text": 4, "pdf": 5}

    def get_sheet_names(self) -> list:
        return self.excel_handler.get_sheet_names()

    def get_sheet_questions(self, sheet_name: str) -> list:
        data = self.excel_handler.get_sheet_data(sheet_name)
        return [row[0] for row in data]

    def get_file_path(
        self, sheet_name: str, question_index: int, file_format: str
    ) -> str:
        column_index = self.format_column_map.get(file_format)
        if column_index is None:
            return None
        return self.excel_handler.get_cell_value(
            sheet_name, question_index + 2, column_index
        )
