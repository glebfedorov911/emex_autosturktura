from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.api_v1.utils.depends import get_unique_filename

import os
import pandas as pd
import datetime


def check_format(filename):
    directory, ext = os.path.splitext(filename)
    if not (ext in (".xlsx", '.xls')):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Плохой формат файла"
        )

async def save_file(file: UploadFile):
    directory = settings.proxy.path_for_upload
    filename = get_unique_filename(directory, file.filename)
    file_location = os.path.join(directory, filename)

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    return file_location

async def get_data(file_location):
    data = pd.read_excel(file_location).values.tolist()
    return data

def check_correct_date(date):
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    except:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Некорректная дата | Incorrect date"
        )
    
    return date

def check_same_file(filename):
    shbl = pd.read_excel(os.path.join(settings.proxy.path_for_upload, "shablon.xlsx"))
    filename = pd.read_excel(os.path.join(settings.proxy.path_for_upload, filename))

    shbl_keys = list(shbl.keys())
    filename_keys = list(filename.keys())

    return filename_keys == shbl_keys