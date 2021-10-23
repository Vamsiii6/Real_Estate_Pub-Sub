from flask import Flask, request, abort
from flask_cors import CORS
from pypika import Table, MySQLQuery, Order, functions
import firebase_admin
from functools import wraps
from firebase_admin import credentials, auth
import pymysql.cursors
from flask_socketio import SocketIO
import requests
import threading
import time

# Firebase Instantiation
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "ds-project1-186c7-firebase-adminsdk-vqoyz-b5e74dceac.json")
    firebase_admin.initialize_app(cred)


# Init Flask app with cors
app = Flask(__name__)
CORS(app)

# Web socket Initialization
socketio = SocketIO(app, cors_allowed_origins='*')
socketio.run(app)

# Connection to MySQL
config = {"host": "db", "user": "root", "password": "root", "database": "ds_project1", "port": 3306,
          "cursorclass": pymysql.cursors.DictCursor}
app.config['PROPAGATE_EXCEPTIONS'] = False


# Seperate thread to communicate with broker container
class brokerThread(threading.Thread):
    def __init__(self, name, payload_, url):
        threading.Thread.__init__(self)
        self.name = name
        self.payload_ = payload_
        self.url = url

    def run(self):
        time.sleep(5)
        # Inform broker about new event
        res = requests.post(f"http://broker:5001/broker/{self.url}",
                            json=self.payload_, timeout=600)
        app.logger.info(res.json())


# Decorator for API Auth validation using Firebase auth manager
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


# Return the list of all properties data from the Property table based on mode
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

# Adds new entry to the properties table in the database and informs broker about the event


@ app.route("/api/publishProperty", methods=["POST"])
@ login_required
def createNewProperty(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        properties = Table('properties')
        input_vals = input_json['properties']
        users_table = Table('users')
        q4 = MySQLQuery.from_(users_table).select(
            'name').where(users_table.uid == user_id)
        cursor.execute(q4.get_sql())
        user_obj = cursor.fetchone()
        created_by_name = user_obj['name']
        insert_val = (input_vals['name'],
                      input_vals['description'], input_vals['price'], input_vals['city_id'], input_vals['room_type_id'], user_id, created_by_name)
        q = MySQLQuery.into(properties).columns(
            'name', 'description', 'price', 'city_id', 'room_type_id', 'created_by_uid', 'created_by_name').insert(insert_val)
        cursor.execute(q.get_sql())
        cursor.close()
    connection.commit()
    connection.close()
    broker_thread = brokerThread(
        "ds-broker", {"property": {**input_vals, "created_by_uid": user_id, "created_by_name": created_by_name}}, "notify")
    broker_thread.start()

    return input_vals

# Adds new entry to the user table


@ app.route("/api/addNewUser", methods=["POST"])
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

# Manage Subscription list of user (Subscibe/Unsubscribe)


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

# Manage Advertisements list of user (Advertise/Deadvertise)


@app.route("/api/manageAdvertisements", methods=["POST"])
@login_required
def manageAdvertisements(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        adv_cities_rel_vals = input_json['adv_cities_rel']
        adv_room_types_rel_vals = input_json['adv_room_types_rel']
        adv_cities_rel_table = Table('adv_cities_rel')
        room_types_rel_table = Table('adv_room_types_rel')
        q_del1 = MySQLQuery.from_(adv_cities_rel_table).delete().where(
            adv_cities_rel_table.uid == user_id)
        q_del2 = MySQLQuery.from_(room_types_rel_table).delete().where(
            room_types_rel_table.uid == user_id)
        cursor.execute(q_del1.get_sql())
        cursor.execute(q_del2.get_sql())
        if len(adv_cities_rel_vals) > 0:
            for val in adv_cities_rel_vals:
                insert_val = (val, user_id)
                q1 = MySQLQuery.into(adv_cities_rel_table).columns(
                    'city_id', 'uid').insert(insert_val)
                cursor.execute(q1.get_sql())
        if len(adv_room_types_rel_vals) > 0:
            for val in adv_room_types_rel_vals:
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

# Get all user advertisements


@app.route("/api/getAllAvertisements", methods=["GET"])
@login_required
def getAllAvertisements(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        adv_cities_rel_table = Table('adv_cities_rel')
        room_types_rel_table = Table('adv_room_types_rel')
        q1 = MySQLQuery.from_(adv_cities_rel_table).select('id', 'city_id').where(
            adv_cities_rel_table.uid == user_id)
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

# Trigger real api to fetch and sync data.


@app.route("/api/triggerRapidApi", methods=["GET"])
@login_required
def triggerRapidApi(user_id):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        url = "https://us-real-estate.p.rapidapi.com/v2/for-sale"

        querystring = {"offset": "0", "limit": "20",
                       "state_code": "NY", "city": "Buffalo", "sort": "newest"}

        headers = {
            'x-rapidapi-host': "us-real-estate.p.rapidapi.com",
            'x-rapidapi-key': "794a2152c5msh2b0ef914247c640p165355jsnd8fd78983d6f"
        }

        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        # f = open('input_api.json',)
        # data = json.load(f)
        users_table = Table('users')
        q4 = MySQLQuery.from_(users_table).select(
            'name').where(users_table.uid == user_id)
        cursor.execute(q4.get_sql())
        user_obj = cursor.fetchone()
        created_by_name = user_obj['name']
        inserted_room_types = []
        # for record in data.get("data", {}).get("home_search", {}).get("results", []):
        for record in response.json().get("data", {}).get("home_search", {}).get("results", []):
            insert_rec = {}
            insert_rec['image_url'] = record.get(
                "primary_photo", {}).get("href", '').replace("\\", "")
            insert_rec['price'] = record.get("list_price", 0)
            if record.get("listing_id", '') != '':
                insert_rec['listing_id'] = record.get("listing_id", '')
            insert_rec['city_id'] = 1
            insert_rec['description'] = record.get(
                "branding", [])[0].get("name", '')
            insert_rec['room_type_id'] = record.get(
                "description", {}).get("beds", 1)
            insert_rec['name'] = record.get(
                "location", {}).get("address", {}).get("line", {})
            insert_rec['listing_id'] = record.get(
                "listing_id", '')
            properties = Table('properties')
            insert_val = (insert_rec['name'],
                          insert_rec['description'], insert_rec['price'], insert_rec['city_id'], insert_rec['room_type_id'], user_id, created_by_name, insert_rec['image_url'], insert_rec['listing_id'])
            q = MySQLQuery.into(properties).columns(
                'name', 'description', 'price', 'city_id', 'room_type_id', 'created_by_uid', 'created_by_name', 'image_url', 'listing_id').insert(insert_val)
            q_p = MySQLQuery.from_(properties).select(
                'id').where(properties.listing_id == insert_rec['listing_id'])
            cursor.execute(q_p.get_sql())
            prop_obj = cursor.fetchone()
            app.logger.info(prop_obj)
            if prop_obj == None:
                cursor.execute(q.get_sql())
                if not insert_rec['room_type_id'] in inserted_room_types:
                    inserted_room_types.append(insert_rec['room_type_id'])
        if len(inserted_room_types) > 0:
            broker_thread = brokerThread(
                "ds-broker-bulk", {"city_id": 1, "room_types": inserted_room_types, "uid": user_id, "user_name": created_by_name}, "notifyBulk")
            broker_thread.start()
        cursor.close()
    connection.commit()
    connection.close()
    return {"success": 1}
