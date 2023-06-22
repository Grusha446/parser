from flask import Flask, jsonify, request, render_template
import json
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, or_
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
            return f"<AccessLog(id='{self.id}', ip='{self.ip}', date='{self.date}', protocol='{self.protocol}', status_code='{self.status_code}')>"

    Session = sessionmaker(bind=engine)

except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    exit()

app = Flask(__name__)

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        session = Session()

        query = session.query(AccessLog)

        filter_ip = request.args.get('ip')
        filter_start_date = request.args.get('start_date')
        filter_end_date = request.args.get('end_date')

        if filter_ip:
            query = query.filter(AccessLog.ip == filter_ip)
        if filter_start_date and filter_end_date:
            query = query.filter(AccessLog.date >= filter_start_date, AccessLog.date <= filter_end_date)
        elif filter_start_date:
            query = query.filter(AccessLog.date >= filter_start_date)
        elif filter_end_date:
            query = query.filter(AccessLog.date <= filter_end_date)

        result = query.all()

        logs = []
        for row in result:
            log = {
                'id': row.id,
                'ip': row.ip,
                'date': row.date.strftime("%Y-%m-%d %H:%M:%S")
            }
            logs.append(log)

        session.close()

        return render_template('logs.html', logs=logs)
    except Exception as e:
        print(f"Error occurred in the application: {e}")
        return jsonify({'error': 'internal server error'}), 500

if __name__ == '__main__':
    app.run()