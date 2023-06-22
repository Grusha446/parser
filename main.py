import re
import datetime
import json
import click
import datetime
import argparse
import configparser

from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

with open('config.json') as f:
    data = json.load(f)

db_config = data['database']
try:
    engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['name']}")
    metadata = MetaData()
    metadata.bind = engine
    Base = declarative_base()
    # Создаем класс для таблицы
    class AccessLog(Base):
        __tablename__ = 'access_logs'
        id = Column(Integer, primary_key=True)
        ip = Column(String(255))
        date = Column(DateTime)
        protocol = Column(String(1000))
        status_code = Column(Integer)

        def __repr__(self):
            return f"<Логи(id='{self.id}', ip='{self.ip}', date='{self.date}', protocol='{self.protocol}', status_code='{self.status_code}')>"

    # Создаем таблицу
    Base.metadata.create_all(engine)

except Exception as e:
    print(f"Ошибка подключения к MySql: {e}")
    exit()

# Парсим логи
logs = "access.log"
pattern = r'(\d+\.\d+\.\d+\.\d+)\s-\s-\s\[(.*?)\]\s\"(.*?)\"\s(\d+)'

try:
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(logs, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                date_str = match.group(2)
                protocol = match.group(3)
                status_code = match.group(4)

                date = datetime.datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S %z")

                # Сохранение данных в БД
                log = AccessLog(ip=ip, date=date, protocol=protocol, status_code=status_code)
                session.add(log)

    session.commit()

except FileNotFoundError as e:
    print(f"Файл логов не найден: {e}")
    exit()

def view_logs(ip=None, start_date=None, end_date=None, log_path=None, logs_mask=None):
    from sqlalchemy import and_

    # Формируем SQL-запрос в соответствии с переданными параметрами
    query = session.query(AccessLog)

    if ip:
        query = query.filter(AccessLog.ip == ip)
    if start_date and end_date:
        query = query.filter(and_(AccessLog.date >= start_date, AccessLog.date <= end_date))
    elif start_date:
        query = query.filter(AccessLog.date >= start_date)
    elif end_date:
        query = query.filter(AccessLog.date <= end_date)

    # Извлекаем результаты запроса и выводим на экран
    try:
        res = query.all()
        for r in res:
            print(r)
    except Exception as e:
        print(f"Ошибка получения данных из MySql: {e}")
        exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter logs by IP and/or date')
    parser.add_argument('--ip', type=str, help='Filter logs by IP')
    parser.add_argument('--start-date', type=str, help='Start date for date range filter (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for date range filter (YYYY-MM-DD)')
    parser.add_argument('--config-file', type=str, help='Path to the config file')

    args = parser.parse_args()

    if args.config_file:
        try:
            config = configparser.ConfigParser()
            config.read(args.config_file)
            log_path = config.get('Server', 'log_path')
            logs_mask = config.get('Server', 'logs_mask')
            view_logs(args.ip, args.start_date, args.end_date, log_path, logs_mask)
        except configparser.Error as e:
            print(f"Ошибка чтения файла: {e}")
            exit()
    else:
        view_logs(args.ip, args.start_date, args.end_date)

session.close()
