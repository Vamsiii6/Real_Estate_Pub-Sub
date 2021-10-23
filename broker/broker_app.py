from flask import Flask, request, abort
from flask_cors import CORS
import os
from pypika import Table, MySQLQuery
import pymysql.cursors
from flask_socketio import SocketIO

# Flask with cors
app = Flask(__name__)
CORS(app)

# Web socket Initialization
socketio = SocketIO(app, cors_allowed_origins='*')
socketio.run(app)

# Connect to MySQL
mysql_password = os.getenv('SQL_PASSWORD')
mysql_user = os.getenv('SQL_USER')
mysql_db = os.getenv('DB_NAME')
mysql_host = os.getenv('DB_NAME')
config = {"host": "db", "user": "root", "password": "root", "database": "ds_project1", "port": 3306,
          "cursorclass": pymysql.cursors.DictCursor}
app.config['PROPAGATE_EXCEPTIONS'] = False


# Notify clients
@app.route("/broker/notify", methods=["POST"])
def notifyUsers():
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        p = input_json['property']
        q1 = f"select C.uid from user_cities_rel as C inner join user_room_types_rel as R on R.uid = C.uid  where C.city_id = {p['city_id']} and R.room_type_id = {p['room_type_id']}"
        cursor.execute(q1)
        result1 = cursor.fetchall()
        q2 = f"select C.uid from user_cities_rel as C  where not exists (select R.uid from user_room_types_rel as R where R.uid = C.uid) and C.city_id = {p['city_id']}"
        cursor.execute(q2)
        result2 = cursor.fetchall()
        q3 = f"select R.uid from user_room_types_rel as R  where not exists (select C.uid from user_cities_rel as C where R.uid = C.uid) and R.room_type_id= {p['room_type_id']}"
        cursor.execute(q3)
        result3 = cursor.fetchall()
        city_table = Table('cities')
        q5 = MySQLQuery.from_(city_table).select(
            'name').where(city_table.id == p['city_id'])
        cursor.execute(q5.get_sql())
        city = cursor.fetchone()
        room_type_table = Table('room_type')
        q6 = MySQLQuery.from_(room_type_table).select(
            'type').where(room_type_table.id == p['room_type_id'])
        cursor.execute(q6.get_sql())
        room_type = cursor.fetchone()
        final_tuple = (*result1, *result2, *result3)
        if len(final_tuple) > 0:
            for user in final_tuple:
                if user == p['created_by_uid']:
                    continue
                payload = {'property': p, 'publisher': p['created_by_name']}
                if user in result1:
                    payload['topic_meta'] = {
                        'city': city['name'], 'room_type': room_type['type']}
                elif user in result2:
                    payload['topic_meta'] = {'city': city['name']}
                else:
                    payload['topic_meta'] = {'room_type': room_type['type']}
                try:
                    socketio.emit(f"socket-{user['uid']}", payload)
                except:
                    app.logger.info(f"{user['uid']} - User not active")
        cursor.close()
    connection.close()
    return {"response": "success"}


# Websocket event from Client
@socketio.on('client-event')
def handle_my_custom_event(data):
    print(f"Client Event {data}")
