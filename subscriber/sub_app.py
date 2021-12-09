from flask import Flask, request, abort
from flask_cors import CORS
import os
from pypika import Table, MySQLQuery, Order, functions
import firebase_admin
from functools import wraps
from firebase_admin import credentials, auth
import pymysql.cursors
from flask_socketio import SocketIO
from kafka import KafkaConsumer
from json import loads
import threading

# Firebase Instantiation
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "ds-project1-186c7-firebase-adminsdk-vqoyz-b5e74dceac.json")
    firebase_admin.initialize_app(cred)


# Flask with cors
app = Flask(__name__)
CORS(app)


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


consumer = KafkaConsumer(
    bootstrap_servers=['kafka1:9093'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)


# Decorator for API Auth validation using Firebase auth Manager


def login_required(func):
    @wraps(func)
    def validate_token(*args, **kwargs):
        auth_head = request.headers["authorization"]
        user_id = ''
        if not auth_head:
            abort(403)
        else:
            token = auth_head.split("Bearer:")[1]
        try:
            auth_res = auth.verify_id_token(id_token=token, check_revoked=True)
            user_id = auth_res['user_id']

        except Exception as error:
            if isinstance(error, auth.ExpiredIdTokenError):
                abort(401)
            else:
                abort(500)
        return func(user_id, *args, **kwargs)
    return validate_token


# Return the list of all properties data from the Property table
@app.route("/api/getAllProperty", methods=["GET"])
@login_required
def fetchAllProperty(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        properties = Table('properties')
        page = 1
        if (request.args['page']):
            page = request.args['page']
        q = MySQLQuery.from_(properties)
        if request.args['mode'] == 'myown':
            q = q.where(properties.created_by_uid == user_id)
        if request.args['mode'] == 'subscribed':
            q1 = f"select R.room_type_id from user_room_types_rel as R where R.uid = '{user_id}'"
            cursor.execute(q1)
            room_types = cursor.fetchall()
            room_type_ids = tuple(i['room_type_id'] for i in room_types)
            q2 = f"select city_id from user_cities_rel where uid = '{user_id}'"
            cursor.execute(q2)
            city_types = cursor.fetchall()
            city_type_ids = tuple(i['city_id'] for i in city_types)
            if len(room_type_ids) == 0 and len(city_type_ids) == 0:
                q = q.where(properties.id < 0)
            if len(room_type_ids) > 0:
                q = q.where(properties.room_type_id.isin(room_type_ids))
            if len(city_type_ids) > 0:
                q = q.where(properties.city_id.isin(city_type_ids))
            q = q.where((properties.created_by_uid == user_id).negate())
        q_final = q.select('id', 'name', 'description', 'price', 'room_type_id', 'city_id',
                           'image_url', 'created_by_name').orderby('id', order=Order.desc).limit(8).offset((int(page)-1)*8)
        q_count = q.select(functions.Count("id").as_('count'))
        cursor.execute(q_final.get_sql())
        results = cursor.fetchall()
        result_ = {"records": results}
        if request.args['with_count'] == 'true':
            cursor.execute(q_count.get_sql())
            count = cursor.fetchone()
            result_['count'] = count['count']
        cursor.close()
    connection.close()
    return result_


# Manage Subscription list of user


@app.route("/api/manageSubscriptions", methods=["POST"])
@login_required
def manageSubscriptions(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        user_cities_rel_vals = input_json['user_cities_rel']
        user_room_types_rel_vals = input_json['user_room_types_rel']
        user_cities_rel_table = Table('user_cities_rel')
        room_types_rel_table = Table('user_room_types_rel')
        q_del1 = MySQLQuery.from_(user_cities_rel_table).delete().where(
            user_cities_rel_table.uid == user_id)
        q_del2 = MySQLQuery.from_(room_types_rel_table).delete().where(
            room_types_rel_table.uid == user_id)
        cursor.execute(q_del1.get_sql())
        cursor.execute(q_del2.get_sql())
        if len(user_cities_rel_vals) > 0:
            for val in user_cities_rel_vals:
                insert_val = (val, user_id)
                q1 = MySQLQuery.into(user_cities_rel_table).columns(
                    'city_id', 'uid').insert(insert_val)
                cursor.execute(q1.get_sql())
        if len(user_room_types_rel_vals) > 0:
            for val in user_room_types_rel_vals:
                insert_val = (val, user_id)
                q2 = MySQLQuery.into(room_types_rel_table).columns(
                    'room_type_id', 'uid').insert(insert_val)
                cursor.execute(q2.get_sql())
        cursor.close()
    connection.commit()
    connection.close()
    return {"done": 1}


# Get all user subscriptions


@app.route("/api/getAllSubscriptions", methods=["GET"])
@login_required
def getAllSubscriptions(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        user_cities_rel_table = Table('user_cities_rel')
        room_types_rel_table = Table('user_room_types_rel')
        q1 = MySQLQuery.from_(user_cities_rel_table).select('id', 'city_id').where(
            user_cities_rel_table.uid == user_id)
        cursor.execute(q1.get_sql())
        cities_rel = cursor.fetchall()
        q2 = MySQLQuery.from_(room_types_rel_table).select('id', 'room_type_id').where(
            room_types_rel_table.uid == user_id)
        cursor.execute(q2.get_sql())
        rooms_rel = cursor.fetchall()
        cursor.close()
    connection.close()
    return {"cities": cities_rel, "room_types": rooms_rel}

# Fetch all cities


@app.route("/api/getAllCities", methods=["GET"])
@login_required
def getAllCities(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        cities_table = Table('cities')
        q1 = MySQLQuery.from_(cities_table).select('id', 'name')
        cursor.execute(q1.get_sql())
        cities = cursor.fetchall()
        cursor.close()
    connection.close()
    return {"cities": cities}

# Fetch all room types


@app.route("/api/getAllRoomTypes", methods=["GET"])
@login_required
def getAllRoomTypes(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        room_type_table = Table('room_type')
        q1 = MySQLQuery.from_(room_type_table).select('id', 'type')
        cursor.execute(q1.get_sql())
        roomTypes = cursor.fetchall()
        cursor.close()
    connection.close()
    return {"roomTypes": roomTypes}

# Fetch User Details from Database


@app.route("/api/getUserDetail", methods=["GET"])
@login_required
def fetchUserDetail(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        users_table = Table('users')
        q = MySQLQuery.from_(users_table).select(
            'name', 'email', 'phone', 'roles', 'uid').where(users_table.uid == user_id)
        cursor.execute(q.get_sql())
        results = cursor.fetchone()
        cursor.close()
    connection.close()
    return {"userDetails": results}

# Web socket emit to client to inform about new events


def notifySubscriber(input_json):
    informed_user = []
    results_map = input_json["users_list"]
    result1 = results_map["type"]
    result2 = results_map["city"]
    result3 = results_map["both"]
    mode = input_json["mode"]
    final_tuple = (*result1, *result2, *result3)
    if len(final_tuple) > 0:
        for user in final_tuple:
            payload = {}
            if mode == 'bulk':
                publisher = input_json["publisher"]
                payload = {
                    'publisher': publisher['name'], "mode": "bulk", "partition": input_json["partition"]}
                if user == publisher['uid'] or user['uid'] in informed_user:
                    continue
            else:
                topic_meta = input_json["topic_meta"]
                property_info = input_json["property"]
                payload = {'property': property_info,
                           'publisher': property_info['created_by_name'], "partition": input_json["partition"]}
                if user == property_info['created_by_uid'] or user['uid'] in informed_user:
                    continue
                if user in result1:
                    payload['topic_meta'] = {
                        'city': topic_meta['city'], 'room_type': topic_meta['room_type']}
                elif user in result2:
                    payload['topic_meta'] = {'city': topic_meta['city']}
                else:
                    payload['topic_meta'] = {
                        'room_type': topic_meta['room_type']}
            # try:
            socketio.emit(f"socket-{user['uid']}", payload)
            informed_user.append(user['uid'])
            # except:
            #     app.logger.info(f"{user['uid']} - User not active")
    return {"success": "done"}


def notifyClient(data, partition):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        payload = {}
        if data['mode'] == 'single':
            p = data['property']
            q1 = f"select C.uid from user_cities_rel as C inner join user_room_types_rel as R on R.uid = C.uid  where C.city_id = {p['city_id']} and R.room_type_id = {p['room_type_id']}"
            cursor.execute(q1)
            result1 = cursor.fetchall()
            q2 = f"select C.uid from user_cities_rel as C where not exists (select R.uid from user_room_types_rel as R where R.uid = C.uid) and C.city_id = {p['city_id']}"
            cursor.execute(q2)
            result2 = cursor.fetchall()
            q3 = f"select R.uid from user_room_types_rel as R where not exists (select C.uid from user_cities_rel as C where R.uid = C.uid) and R.room_type_id= {p['room_type_id']}"
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
            payload = {"users_list": {"type": result1, "city": result2, "both": result3}, "topic_meta": {
                'city': city['name'], 'room_type': room_type['type']}, "property": p, "mode": "single", "partition": partition}
        elif data['mode'] == 'bulk':
            c_id = data['city_id']
            r_ids = data['room_types']
            uid_ = data['uid']
            user_name = data['user_name']
            q2 = f"select C.uid from user_cities_rel as C where not exists (select R.uid from user_room_types_rel as R where R.uid = C.uid) and C.city_id = {c_id}"
            cursor.execute(q2)
            result2 = cursor.fetchall()
            result1 = ()
            result3 = ()
            for r_id in r_ids:
                q1 = f"select C.uid from user_cities_rel as C inner join user_room_types_rel as R on R.uid = C.uid  where C.city_id = {c_id} and R.room_type_id = {r_id}"
                cursor.execute(q1)
                r1 = cursor.fetchall()
                q3 = f"select R.uid from user_room_types_rel as R where not exists (select C.uid from user_cities_rel as C where R.uid = C.uid) and R.room_type_id= {r_id}"
                cursor.execute(q3)
                r3 = cursor.fetchall()
                result1 = (*result1, *r1)
                result3 = (*result3, *r3)
            payload = {"users_list": {"type": result1, "city": result2, "both": result3},
                       "publisher": {"uid": uid_, "name": user_name}, "mode": "bulk", "partition": partition}
        notifySubscriber(payload)
        cursor.close()
    connection.close()
    return {"success": data}


class consumerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Web socket Initialization
        consumer.subscribe(['Buffalo', 'Syracuse', 'Albany', 'NYC'])
        for event in consumer:
            app.logger.info(event)
            event_data = event.value
            notifyClient(event_data, event.partition)


consumer_thread = consumerThread()
consumer_thread.start()
