
from flask import Flask, request
from flask_cors import CORS

import mysql.connector
app = Flask(__name__)
CORS(app)
config = {"host": "db", "user": "root", "password": "root", "database": "ds_project1", "port": "3306"}
con = mysql.connector.connect(**config)

@app.route("/api/getAllProperty", methods=["GET"])
def getAllProperty():
    cur = con.cursor()
    cur.execute("select * from property")
    field_names = [i[0] for i in cur.description]
    results = cur.fetchall()
    cur.close()
    allrecords = []
    for record in results:
        formatted_record = {}
        for index,field in enumerate(field_names):
            formatted_record[field] = record[index]
        allrecords.append(formatted_record)
    return {"records":allrecords}

@app.route("/api/addNewProperty", methods=["POST"])
def createNewProperty():
    cur = con.cursor()
    input_json = request.get_json(force=True)
    property = input_json['property']
    insert_val = (property['name'], property['description'], property['price'])
    cur.execute("INSERT INTO property (name, description, price) values(%s, %s, %s)", insert_val)
    con.commit()
    cur.close()
    return property
