from flask import Flask, request, abort
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pypika import Table, MySQLQuery
import firebase_admin
from functools import wraps
from firebase_admin import credentials, auth
import pymysql.cursors
import threading
import time
from flask_socketio import SocketIO

# Firebase Instantiation
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "ds-project1-186c7-firebase-adminsdk-vqoyz-b5e74dceac.json")
    firebase_admin.initialize_app(cred)

# ENV Variables
load_dotenv()

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


# Sample Broker thread
# class brokerThread(threading.Thread):
#     def __init__(self, name):
#         threading.Thread.__init__(self)
#         self.name = name

#     def run(self):
#         time.sleep(10)
#         # Web socket event to client
#         socketio.emit('testing-event', {'data': 'foobar'})
#         print(f"print args in thread {self.name}")


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
        q = MySQLQuery.from_(properties).select(
            'id', 'name', 'description', 'price', 'room_type_id', 'city_id', 'image_url')
        if request.args['mode'] == 'all':
            q = q.where(properties.created_by == user_id)
        cursor.execute(q.get_sql())
        results = cursor.fetchall()
        cursor.close()
    connection.close()
    return {"records": results}


# Adds new entry to the Property table in the database
@app.route("/api/addNewProperty", methods=["POST"])
@login_required
def createNewProperty(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        properties = Table('properties')
        input_vals = input_json['properties']
        insert_val = (input_vals['name'],
                      input_vals['description'], input_vals['price'], input_vals['city_id'], input_vals['room_type_id'], user_id)
        q = MySQLQuery.into(properties).columns(
            'name', 'description', 'price', 'city_id', 'room_type_id', 'created_by').insert(insert_val)
        cursor.execute(q.get_sql())
        cursor.close()
    connection.commit()
    connection.close()

    return input_vals

# Adds new entry to the User table


@app.route("/api/addNewUser", methods=["POST"])
def createNewUser():
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        users_table = Table('users')
        input_vals = input_json['userDetails']
        insert_val = (input_vals['name'], input_vals['email'],
                      input_vals['phone'], input_vals['roles'], input_vals['uid'])
        q = MySQLQuery.into(users_table).columns(
            'name', 'email', 'phone', 'roles', 'uid').insert(insert_val)
        cursor.execute(q.get_sql())
        cursor.close()
    connection.commit()
    connection.close()
    return input_vals

# Fetch User Details


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


# Websocket event from Client
@socketio.on('client-event')
def handle_my_custom_event(data):
    print(f"Client Event {data}")
