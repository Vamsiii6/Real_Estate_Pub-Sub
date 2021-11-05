from flask import Flask, request
from flask_cors import CORS
from pypika import Table, MySQLQuery, Order
import pymysql.cursors
from flask_socketio import SocketIO
import requests
import threading
# Flask with cors
app = Flask(__name__)
CORS(app)

# Web socket Initialization
socketio = SocketIO(app, cors_allowed_origins='*')
socketio.run(app)

# Connect to MySQL
config = {"host": "db", "user": "root", "password": "root", "database": "ds_project1", "port": 3306,
          "cursorclass": pymysql.cursors.DictCursor}
app.config['PROPAGATE_EXCEPTIONS'] = False
portVsServer = {"5005": 1, "5006": 2, "5007": 3,  "5008": 4}

# To get the port of Broker app


def getCurrentPort():
    sn_port = None
    server_name = request.host
    if server_name:
        sn_host, temp_, sn_port = server_name.partition(":")
    return sn_port

# This is similar to matchlist in rendevous check if the node is responsible for the topic


def isResponsibleForTopic(city_id, current_port):
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        bt_table = Table('broker_vs_topics')
        q_b = MySQLQuery.from_(bt_table).select('broker_port').where(
            (bt_table.topic_id == city_id) & (bt_table.broker_port == current_port)).orderby('broker_port', order=Order.asc)
        cursor.execute(q_b.get_sql())
        result = cursor.fetchone()
        if result is not None and current_port == result['broker_port']:
            return True
    return False

# If not responsible for the topic the broker will inform Nearby Responsible Broker nodes to check for the match


class informResponsibleBrokers(threading.Thread):
    def __init__(self, name, payload_, current_port):
        threading.Thread.__init__(self)
        self.name = name
        self.payload_ = payload_
        self.current_port = current_port

    def run(self):
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            bt_table = Table('broker_vs_topics')
            q_b = MySQLQuery.from_(bt_table).select('broker_port').where(
                bt_table.topic_id == self.payload_['property']['city_id']).orderby('broker_port', order=Order.asc)
            cursor.execute(q_b.get_sql())
            available_brokers = cursor.fetchall()
            for broker in available_brokers:
                if int(broker['broker_port']) <= int(self.current_port):
                    continue
                try:
                    res = requests.post(f"http://broker{portVsServer[broker['broker_port']]}:{broker['broker_port']}/broker/notify",
                                        json=self.payload_, timeout=600)
                    if res:
                        app.logger.info("Break Loop")
                        break
                except Exception as err:
                    app.logger.error(f"Warning {err}")
                    pass
            cursor.close()
        connection.close()


# Notify users based on subscription for the added property
@app.route("/broker/notify", methods=["POST"])
def notifyUsers():
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        p = input_json['property']
        current_port = getCurrentPort()
        if not isResponsibleForTopic(p['city_id'], current_port):
            app.logger.info("Not Responsible broker informing other brokers")
            new_thread = informResponsibleBrokers(
                "inform-broker", input_json, current_port)
            new_thread.start()
            return {"error": "not responsible for topic"}
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
        sn_port = getCurrentPort()
        payload = {"users_list": {"type": result1, "city": result2, "both": result3}, "topic_meta": {
            'city': city['name'], 'room_type': room_type['type']}, "broker_port": sn_port, "property": p, "mode": "single"}
        requests.post(f"http://subscriber:5002/api/notifySubscriber",
                      json=payload, timeout=600)
        cursor.close()
    connection.close()
    return {"response": "success"}

# Notify users based on subscription for the added properties


@app.route("/broker/notifyBulk", methods=["POST"])
def notifyBulk():
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        input_json = request.get_json(force=True)
        c_id = input_json['city_id']
        r_ids = input_json['room_types']
        uid_ = input_json['uid']
        user_name = input_json['user_name']
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
        server_name = request.host
        sn_port = None
        if server_name:
            sn_host, temp_, sn_port = server_name.partition(":")
        payload = {"users_list": {"type": result1, "city": result2, "both": result3},
                   "publisher": {"uid": uid_, "name": user_name}, "broker_port": sn_port, "mode": "bulk"}
        requests.post(f"http://subscriber:5002/api/notifySubscriber",
                      json=payload, timeout=600)
        cursor.close()
    connection.close()
    return {"response": "success"}
