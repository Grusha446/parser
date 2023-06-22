import re
import datetime
import mysql.connector
import json
import click
import datetime
import argparse
import configparser

# Подключаемся к БД
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="PA$$vv0RD",
    database="final"
)

# Создаем таблицу
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS access_logs (id INT AUTO_INCREMENT PRIMARY KEY, ip VARCHAR(255), date DATETIME, user_agent VARCHAR(1000), status_code INT)")

# Парсим логи
logs = "access.log"
pattern = r'(\d+\.\d+\.\d+\.\d+)\s-\s-\s\[(.*?)\]\s\"(.*?)\"\s(\d+)'

with open(logs, 'r') as file:
    for line in file:
        match = re.search(pattern, line)
        if match:
            ip = match.group(1)
            date_str = match.group(2)
            user_agent = match.group(3)
            status_code = match.group(4)

            date = datetime.datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S %z")

            # Сохранение данных в БД
            sql = "INSERT INTO access_logs (ip, date, user_agent, status_code) VALUES (%s, %s, %s, %s)"
            values = (ip, date, user_agent, status_code)
            cursor.execute(sql, values)
            

db.commit()

def view_logs(ip=None, start_date=None, end_date=None, log_path=None, logs_mask=None):
    # Формируем SQL-запрос в соответствии с переданными параметрами
    sql_query = 'SELECT * FROM access_logs'
    conditions = []

    if ip:
        conditions.append(f"ip = '{ip}'")
    if start_date and end_date:
        conditions.append(f"date BETWEEN '{start_date}' AND '{end_date}'")
    elif start_date:
        conditions.append(f"date >= '{start_date}'")
    elif end_date:
        conditions.append(f"date <= '{end_date}'")

    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)

    # Выполняем SQL-запрос
    cursor.execute(sql_query)

    # Извлекаем результаты запроса и выводим на экран
    res = cursor.fetchall()
    for r in res:
        print(r)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter logs by IP and/or date')
    parser.add_argument('--ip', type=str, help='Filter logs by IP')
    parser.add_argument('--start-date', type=str, help='Start date for date range filter (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for date range filter (YYYY-MM-DD)')
    parser.add_argument('--config-file', type=str, help='Path to the config file')

    args = parser.parse_args()

    if args.config_file:
        config = configparser.ConfigParser()
        config.read(args.config_file)
        log_path = config.get('Server', 'log_path')
        logs_mask = config.get('Server', 'logs_mask')
        view_logs(args.ip, args.start_date, args.end_date, log_path, logs_mask)
    else:
        view_logs(args.ip, args.start_date, args.end_date)