from flask import Flask, jsonify, request
import json
import mysql.connector

#Подключение к БД
db = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="PA$$vv0RD",
  database="final"
)
#################################################################################
app = Flask(__name__)
#получения данных в формате JSON
@app.route('/logs', methods=['GET'])
def get_logs():
    cursor = db.cursor()
    sql = "SELECT * FROM access_logs"
    conditions = []

    filter_ip = request.args.get('ip')
    filter_start_date = request.args.get('start_date')
    filter_end_date = request.args.get('end_date')

    if filter_ip:
        conditions.append("ip = %s")
    if filter_start_date:
        conditions.append("date >= %s")
    if filter_end_date:
        conditions.append("date <= %s")

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    values = []
    if filter_ip:
        values.append(filter_ip)
    if filter_start_date:
        values.append(filter_start_date)
    if filter_end_date:
        values.append(filter_end_date)

    cursor.execute(sql, tuple(values))
    result = cursor.fetchall()

    logs = []
    for row in result:
        log = {
            'id': row[0],
            'ip': row[1],
            'date': row[2].strftime("%Y-%m-%d %H:%M:%S")
        }
        logs.append(log)

    return jsonify(logs)

if __name__ == '__main__':
    app.run()

db.close()