import psycopg2
import os

from datetime import datetime
from psycopg2 import sql
from dotenv import load_dotenv

from app.api_v1.auth.utils import hash_password


load_dotenv()

tables = ["users", "files", "newfilters", "parsers", "proxys"]

db_config = {
    'dbname': os.getenv("DBNAME"),
    'user': os.getenv("USER"),
    'password': os.getenv("PASSWORD"),
    'host': os.getenv("HOST"),
    'port': os.getenv("PORT"),      
}

def execute_query(conn, query, params=None):
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        conn.commit()

conn = psycopg2.connect(**db_config)

data_add = {
    "files": (
        {"before_parsing_filename": "test1_дляпарсинг.xlsx", "after_parsing_filename": "None", "date": str(datetime.now()), "finish_date": "None", "user_id": "3", "new_filter_id": "None"},
        {"before_parsing_filename": "test1_дляпарсинг.xlsx", "after_parsing_filename": "None", "date": str(datetime.now()), "finish_date": "None", "user_id": "4", "new_filter_id": "None"},
        {"before_parsing_filename": "test1_дляпарсинг.xlsx", "after_parsing_filename": "None", "date": str(datetime.now()), "finish_date": "None", "user_id": "5", "new_filter_id": "None"},
        {"before_parsing_filename": "test2_дляпарсинг.xlsx", "after_parsing_filename": "test2_послепарсинга.xlsx", "date": str(datetime.now()), "finish_date": str(datetime.now()), "user_id": "4", "new_filter_id": "13"},
        {"before_parsing_filename": "test2_дляпарсинг.xlsx", "after_parsing_filename": "test2_послепарсинга.xlsx", "date": str(datetime.now()), "finish_date": str(datetime.now()), "user_id": "4", "new_filter_id": "13"},
        {"before_parsing_filename": "test2_дляпарсинг.xlsx", "after_parsing_filename": "test2_послепарсинга.xlsx", "date": str(datetime.now()), "finish_date": str(datetime.now()), "user_id": "3", "new_filter_id": "13"},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": "None", "date": str(datetime.now()), "finish_date": "None", "user_id": "3", "new_filter_id": "None"},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": "None", "date": str(datetime.now()), "finish_date": "None", "user_id": "4", "new_filter_id": "None"},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": "None", "date": str(datetime.now()), "finish_date": "None", "user_id": "3", "new_filter_id": "None"},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": "None", "date": str(datetime.now()), "finish_date": "None", "user_id": "5", "new_filter_id": "None"},
    ),
    "users": (
        {"fullname": "admin_fullname", "description": "admin_description", "username": "admin", "password": str(hash_password(os.getenv("ADMIN_PASSWORD"))), "is_admin": "True", "is_parsing": "False"},
        {"fullname": "newuser_fullname", "description": "newuser_description", "username": "newuser", "password": str(hash_password(os.getenv("NEWUSER_PASSWORD"))), "is_admin": "False", "is_parsing": "False"},
        {"fullname": "simpleuser_fullname", "description": "simpleuser_description", "username": "simpleuser", "password": str(hash_password(os.getenv("SIMPLE_PASSWORD"))), "is_admin": "False", "is_parsing": "False"},
    ),
    "newfilters": (
        {"deep_filter": "10", "deep_analog": "10", "analog": "False", "is_bigger": "True", "date": "5", "logo": "HXAW", "user_id": "3", "title": "string1"},
        {"deep_filter": "50", "deep_analog": "25", "analog": "False", "is_bigger": "False", "date": "25", "logo": "MARO", "user_id": "4", "title": "string2"},
        {"deep_filter": "15", "deep_analog": "25", "analog": "True", "is_bigger": "False", "date": "25", "logo": "RXGF", "user_id": "5", "title": "string3"},
        {"deep_filter": "10", "deep_analog": "25", "analog": "False", "is_bigger": "False", "date": "25", "logo": "RXGF", "user_id": "5", "title": "string4"},
        {"deep_filter": "12", "deep_analog": "1", "analog": "False", "is_bigger": "None", "date": "0", "logo": "RXGF", "user_id": "5", "title": "string5"},
        {"deep_filter": "33", "deep_analog": "31", "analog": "False", "is_bigger": "None", "date": "0", "logo": "RXGF", "user_id": "5", "title": "string6"},
        {"deep_filter": "11", "deep_analog": "23", "analog": "False", "is_bigger": "True", "date": "5", "logo": "OEOL", "user_id": "4", "title": "string7"},
        {"deep_filter": "11", "deep_analog": "10", "analog": "False", "is_bigger": "False", "date": "10", "logo": "OEOL", "user_id": "4", "title": "string8"},
        {"deep_filter": "11", "deep_analog": "10", "analog": "False", "is_bigger": "False", "date": "10", "logo": "RMFZ", "user_id": "3", "title": "string9"},
        {"deep_filter": "11", "deep_analog": "10", "analog": "False", "is_bigger": "False", "date": "10", "logo": "RMFZ", "user_id": "3", "title": "string10"},
    )
}

for table in tables:
    check_query = sql.SQL(f"SELECT COUNT(*) FROM {table}")

    for values in data_add[table]:
        val = ', '.join(["%s"]*len(values.values()))
        insert_query = sql.SQL(f"""
            INSERT INTO {table} ({', '.join(list(values.keys()))})
            VALUES ({val})
        """)

        execute_query(conn, insert_query, list(values.values()))

    with conn.cursor() as cursor:
        cursor.execute(check_query)
        count = cursor.fetchone()[0]
    
    print(count)