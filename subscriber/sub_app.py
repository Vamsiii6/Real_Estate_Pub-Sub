from flask import Flask, request, abort
from flask_cors import CORS
import os
from pypika import Table, MySQLQuery, Order, functions
import firebase_admin
from functools import wraps
from firebase_admin import credentials, auth
import pymysql.cursors
from flask_socketio import SocketIO

# Firebase Instantiation
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "ds-project1-186c7-firebase-adminsdk-vqoyz-b5e74dceac.json")
    firebase_admin.initialize_app(cred)


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
                q = q.where(False)
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


@app.route("/api/notifySubscriber", methods=["POST"])
def notifySubscriber():
    input_json = request.get_json(force=True)
    app.logger.info(input_json)
    informed_user = []
    results_map = input_json["users_list"]
    topic_meta = input_json["topic_meta"]
    property_info = input_json["property"]
    result1 = results_map["type"]
    result2 = results_map["city"]
    result3 = results_map["both"]
    final_tuple = (*result1, *result2, *result3)
    if len(final_tuple) > 0:
        for user in final_tuple:
            if user == property_info['created_by_uid'] or user['uid'] in informed_user:
                continue
            payload = {'property': property_info,
                       'publisher': property_info['created_by_name']}
            if user in result1:
                payload['topic_meta'] = {
                    'city': topic_meta['city'], 'room_type': topic_meta['room_type']}
            elif user in result2:
                payload['topic_meta'] = {'city': topic_meta['city']}
            else:
                payload['topic_meta'] = {'room_type': topic_meta['room_type']}
            try:
                payload["broker"] = input_json["broker_port"]
                socketio.emit(f"socket-{user['uid']}", payload)
                informed_user.append(user['uid'])
            except:
                app.logger.info(f"{user['uid']} - User not active")
    return {"success": "done"}
