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
connection = pymysql.connect(host="db", user="root", password="root", database="ds_project1", port=3306,
                             cursorclass=pymysql.cursors.DictCursor)
app.config['PROPAGATE_EXCEPTIONS'] = False


# Sample Broker thread
class brokerThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        time.sleep(10)
        # Web socket event to client
        socketio.emit('testing-event', {'data': 'foobar'})
        print(f"print args in thread {self.name}")


# Decorator for API Auth validation using Firebase auth Manager
def login_required(f):
    @wraps(f)
    def validate_token(*args, **kwargs):
        auth_head = request.headers["authorization"]
        if not auth_head:
            abort(403)
        else:
            token = auth_head.split("Bearer:")[1]
        try:
            auth.verify_id_token(id_token=token, check_revoked=True)
        except Exception as error:
            if isinstance(error, auth.ExpiredIdTokenError):
                abort(401)
            else:
                abort(500)
        return f(*args, **kwargs)
    return validate_token


# Return the list of all properties data from the Property table
@app.route("/api/getAllProperty", methods=["GET"])
@login_required
def fetchAllProperty():
    with connection.cursor() as cursor:
        q = MySQLQuery.from_('properties').select(
            'id', 'name', 'description', 'price')
        cursor.execute(q.get_sql())
        results = cursor.fetchall()
    return {"records": results}


# Adds new entry to the Property table in the database
@app.route("/api/addNewProperty", methods=["POST"])
@login_required
def createNewProperty():
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        properties = Table('properties')
        input_vals = input_json['properties']
        insert_val = (input_vals['name'],
                      input_vals['description'], input_vals['price'])
        q = MySQLQuery.into(properties).columns(
            'name', 'description', 'price').insert(insert_val)
        cursor.execute(q.get_sql())
    connection.commit()
    broker_thread = brokerThread("ds-broker")
    broker_thread.start()

    return input_vals

# Adds new entry to the User table


@app.route("/api/addNewUser", methods=["POST"])
def createNewUser():
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        users_table = Table('users')
        input_vals = input_json['userDetails']
        insert_val = (input_vals['name'], input_vals['email'],
                      input_vals['phone'], input_vals['roles'], input_vals['uid'])
        q = MySQLQuery.into(users_table).columns(
            'name', 'email', 'phone', 'roles', 'uid').insert(insert_val)
        cursor.execute(q.get_sql())
    connection.commit()
    return input_vals

# Fetch User Details


@app.route("/api/getUserDetail", methods=["POST"])
@login_required
def fetchUserDetail():
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        uid_ = input_json['uid']
        users_table = Table('users')
        q = MySQLQuery.from_('users').select(
            'name', 'email', 'phone', 'roles', 'uid').where(users_table.uid == uid_)
        cursor.execute(q.get_sql())
        results = cursor.fetchone()
    return {"userDetails": results}


# Websocket event from Client
@socketio.on('client-event')
def handle_my_custom_event(data):
    print(f"Client Event {data}")
