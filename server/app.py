from flask import Flask, request, abort
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pypika import Table, MySQLQuery, Field, Parameter
import firebase_admin
from functools import wraps
from firebase_admin import credentials, auth
import pymysql.cursors
import threading
import time


# Firebase Instantiation
cred = credentials.Certificate("ds-project1-186c7-firebase-adminsdk-vqoyz-b5e74dceac.json")
firebase_admin.initialize_app(cred)

# ENV Variables
load_dotenv()

# Flask with cors
app = Flask(__name__)
CORS(app)

# Connect to MySQL
mysql_password = os.getenv('SQL_PASSWORD')
mysql_user = os.getenv('SQL_USER')
mysql_db = os.getenv('DB_NAME')
mysql_host = os.getenv('DB_NAME')
connection = pymysql.connect(host="localhost", user="root", password="root", database="ds_project1", port=3306,
                             cursorclass=pymysql.cursors.DictCursor)



class brokerThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        time.sleep(10)
        print(f"print args in thread {self.name}")



# Decorator for API Auth validation
# using Firebase auth Manager
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
def getAllProperty():
    with connection.cursor() as cursor:
        cursor.execute("select * from properties")
        results = cursor.fetchall()
    return {"records": results}


## Adds new entry to the Property table in the database
@app.route("/api/addNewProperty", methods=["POST"])
def createNewProperty():
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        properties = Table('properties')
        input_vals = input_json['properties']
        insert_val = (input_vals['name'], input_vals['description'], input_vals['price'])
        q = MySQLQuery.into(properties).columns('name', 'description', 'price').insert(insert_val)
        cursor.execute(q.get_sql())
    connection.commit()
    broker_thread = brokerThread("ds-broker")
    broker_thread.start()

    return input_vals




