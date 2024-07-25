from fastapi import HTTPException, status

import datetime


def not_enough_money(response):
    if not response["success"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="У вас недостаточно средств | You haven't got enough money"
        )

def check_correct_date(date):
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Некорректная дата | Incorrect date"
        )
    
    return date