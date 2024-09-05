import psycopg2
import os

from datetime import datetime
from psycopg2 import sql
from dotenv import load_dotenv

from app.api_v1.auth.utils import hash_password
from app.core.config import settings


load_dotenv()

tables = ["files", "parsers", "proxys"]

db_config = {
    'dbname': os.getenv("DBNAME"),
    'user': "postgres",
    'password': os.getenv("PASSWORD"),
    'host': os.getenv("HOST"),
    'port': os.getenv("PORT"),      
}

def execute_query(conn, query, params=None):
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        conn.commit()

conn = psycopg2.connect(**db_config)

def add_to_db(table, data_add):
    check_query = sql.SQL(f"SELECT COUNT(*) FROM {table}")
    with conn.cursor() as cursor:
        cursor.execute(check_query)
        count = cursor.fetchone()[0]

    if count != 0:
        return

    for values in data_add:
        val = ', '.join(["%s"]*len(values.values()))
        insert_query = sql.SQL(f"""
            INSERT INTO {table} ({', '.join(list(values.keys()))})
            VALUES ({val})
        """)

        execute_query(conn, insert_query, list(values.values()))

data_add = {
    "users": (
        {"fullname": "string", "description": "string", "username": "string", "password": bytes(hash_password(os.getenv("string_PASSWORD"))), "is_admin": True, "is_parsing": False},
        {"fullname": "string_admin", "description": "string_admin", "username": "string_admin", "password": bytes(hash_password(os.getenv("string_admin_PASSWORD"))), "is_admin": True, "is_parsing": False},
        {"fullname": "admin_fullname", "description": "admin_description", "username": "admin", "password": bytes(hash_password(os.getenv("ADMIN_PASSWORD"))), "is_admin": True, "is_parsing": False},
        {"fullname": "newuser_fullname", "description": "newuser_description", "username": "newuser", "password": bytes(hash_password(os.getenv("NEWUSER_PASSWORD"))), "is_admin": True, "is_parsing": False},
        {"fullname": "simpleuser_fullname", "description": "simpleuser_description", "username": "simpleuser", "password": bytes(hash_password(os.getenv("SIMPLE_PASSWORD"))), "is_admin": False, "is_parsing": False},
    ),
}

add_to_db("users", data_add["users"])

check_query1 = sql.SQL("SELECT id FROM users WHERE username = 'admin'")
check_query2 = sql.SQL("SELECT id FROM users WHERE username = 'newuser'")
check_query3 = sql.SQL("SELECT id FROM users WHERE username = 'simpleuser'")
with conn.cursor() as cursor:
    cursor.execute(check_query1)
    id_admin_fullname = cursor.fetchone()[0]
    cursor.execute(check_query2)
    id_newuser_fullname = cursor.fetchone()[0]
    cursor.execute(check_query3)
    id_simpleuser_fullname = cursor.fetchone()[0]

data_add = {
    "newfilters": (
        {"deep_filter": "10", "deep_analog": "10", "analog": False, "is_bigger": True, "date": "5", "logo": "HXAW", "user_id": id_admin_fullname, "title": "string1"},
        {"deep_filter": "50", "deep_analog": "25", "analog": False, "is_bigger": False, "date": "25", "logo": "MARO", "user_id": id_newuser_fullname, "title": "string2"},
        {"deep_filter": "15", "deep_analog": "25", "analog": True, "is_bigger": False, "date": "25", "logo": "RXGF", "user_id": id_simpleuser_fullname, "title": "string3"},
        {"deep_filter": "10", "deep_analog": "25", "analog": False, "is_bigger": False, "date": "25", "logo": "RXGF", "user_id": id_simpleuser_fullname, "title": "string4"},
        {"deep_filter": "12", "deep_analog": "1", "analog": False, "logo": "RXGF", "user_id": id_simpleuser_fullname, "title": "string5"},
        {"deep_filter": "33", "deep_analog": "31", "analog": False, "logo": "RXGF", "user_id": id_simpleuser_fullname, "title": "string6"},
        {"deep_filter": "11", "deep_analog": "23", "analog": False, "is_bigger": True, "date": "5", "logo": "OEOL", "user_id": id_newuser_fullname, "title": "string7"},
        {"deep_filter": "11", "deep_analog": "10", "analog": False, "is_bigger": False, "date": "10", "logo": "OEOL", "user_id": id_newuser_fullname, "title": "string8"},
        {"deep_filter": "11", "deep_analog": "10", "analog": False, "is_bigger": False, "date": "10", "logo": "RMFZ", "user_id": id_admin_fullname, "title": "string9"},
        {"deep_filter": "11", "deep_analog": "10", "analog": False, "is_bigger": False, "date": "10", "logo": "RMFZ", "user_id": id_admin_fullname, "title": "string10"},
    ),
}

add_to_db("newfilters", data_add["newfilters"])

check_query4 = sql.SQL("SELECT id FROM newfilters WHERE title = 'string2'")
check_query5 = sql.SQL("SELECT id FROM newfilters WHERE title = 'string9'")
with conn.cursor() as cursor:
    cursor.execute(check_query4)
    id_string2_filter = cursor.fetchone()[0]
    cursor.execute(check_query5)
    id_string9_filter = cursor.fetchone()[0]

for filename in ("test1_дляпарсинг.xlsx", "test2_послепарсинга.xlsx"):
    with open(str(settings.upload.path_for_upload) + "/" + filename, "w") as file:
        file.write("hello world")
        file.close()

data_add = {
    "files": (
        {"before_parsing_filename": "test1_дляпарсинг.xlsx", "after_parsing_filename": None, "date": str(datetime.now()), "user_id": id_admin_fullname},
        {"before_parsing_filename": "test1_дляпарсинг.xlsx", "after_parsing_filename": None, "date": str(datetime.now()), "user_id": id_newuser_fullname},
        {"before_parsing_filename": "test1_дляпарсинг.xlsx", "after_parsing_filename": None, "date": str(datetime.now()), "user_id": id_simpleuser_fullname},
        {"before_parsing_filename": "test2_дляпарсинг.xlsx", "after_parsing_filename": "test2_послепарсинга.xlsx", "date": str(datetime.now()), "user_id": id_newuser_fullname, "new_filter_id": id_string2_filter},
        {"before_parsing_filename": "test2_дляпарсинг.xlsx", "after_parsing_filename": "test2_послепарсинга.xlsx", "date": str(datetime.now()), "user_id": id_newuser_fullname, "new_filter_id": id_string2_filter},
        {"before_parsing_filename": "test2_дляпарсинг.xlsx", "after_parsing_filename": "test2_послепарсинга.xlsx", "date": str(datetime.now()), "user_id": id_admin_fullname, "new_filter_id": id_string9_filter},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": None, "date": str(datetime.now()), "user_id": id_admin_fullname},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": None, "date": str(datetime.now()), "user_id": id_newuser_fullname},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": None, "date": str(datetime.now()), "user_id": id_admin_fullname},
        {"before_parsing_filename": "test3_дляпарсинг.xlsx", "after_parsing_filename": None, "date": str(datetime.now()), "user_id": id_simpleuser_fullname},
    ),
    "parsers": (
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_admin_fullname, "file_id": 1},

        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_newuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_newuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_newuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_newuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_newuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_newuser_fullname, "file_id": 1},


        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_simpleuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_simpleuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_simpleuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_simpleuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_simpleuser_fullname, "file_id": 1},
        {"article": "test_article", "name": "test_name", "brand": "test_brand", "article1": "test_article1", "quantity": "test_quantity", "price": "test_price", "batch": "test_batch",
        "nds": "test_NDS", "best_price": "test_bestPrice", "logo": "test_logo", "delivery_time": "test_deliveryTime", "new_price": "test_newPrice", "quantity1": "test_quantity1",
        "user_id": id_simpleuser_fullname, "file_id": 1},
    ),
    "proxys": (
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "1", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.156.18:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "2", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://94.158.190.15:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "3", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://194.34.248.47:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "4", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.107.162:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "5", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.111.77:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "6", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://95.182.125.155:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "7", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.218.24:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "8", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.11.180:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "9", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://45.15.72.89:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "10", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.137.212:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "11", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.212.217:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "12", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://109.248.14.106:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "13", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.23.195:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "14", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://109.248.166.66:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "15", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.110.75:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "16", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.136.55:1050", "_is_banned": False, "user_id": id_admin_fullname, "is_using": True},

        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "1", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.156.18:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "2", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://94.158.190.15:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "3", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://194.34.248.47:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "4", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.107.162:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "5", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.111.77:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "6", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://95.182.125.155:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "7", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.218.24:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "8", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.11.180:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "9", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://45.15.72.89:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "10", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.137.212:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "11", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.212.217:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "12", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://109.248.14.106:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "13", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.23.195:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "14", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://109.248.166.66:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "15", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.110.75:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "16", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.136.55:1050", "_is_banned": False, "user_id": id_newuser_fullname, "is_using": True},

        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "1", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.156.18:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "2", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://94.158.190.15:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "3", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://194.34.248.47:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "4", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.107.162:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "5", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.111.77:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "6", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://95.182.125.155:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "7", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.218.24:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-09-27 00:00:00", "id_proxy": "8", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.11.180:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "9", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://45.15.72.89:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "10", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.137.212:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "11", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.212.217:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:41:54", "id_proxy": "12", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://109.248.14.106:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "13", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.23.195:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "14", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://109.248.166.66:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "15", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://46.8.110.75:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
        {"expired_at": "2024-10-04 23:01:41", "id_proxy": "16", "login": os.getenv("login_proxy"), "password": os.getenv("password_proxy"), "ip_with_port": "http://188.130.136.55:1050", "_is_banned": False, "user_id": id_simpleuser_fullname, "is_using": True},
    ),
}

for table in tables:
    add_to_db(table, data_add[table])