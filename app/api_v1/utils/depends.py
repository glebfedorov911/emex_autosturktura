from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import NamedStyle


async def edit_file(filepath: str, rows: list):
    wb = load_workbook(filepath)
    ws = wb.active

    integer_style = NamedStyle(name="integer_style", number_format='0')

    for row in rows:
        for cell in ws[row]:  
            if isinstance(cell.value, (int, float)):
                cell.style = integer_style
    
    wb.save(filepath)