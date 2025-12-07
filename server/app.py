#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists')
def get_scientists():

    scientists = [
        s.to_dict(only=("id", "name", "field_of_study")) 
        for s in Scientist.query.all()
        ]

    response = make_response(
        scientists,
        200
    )

    return response

@app.route('/scientists/<int:id>', methods=['GET', 'DELETE'])
def get_scientists_by_id(id):
    scientists_by_id = Scientist.query.filter_by(id=id).first()

    if not scientists_by_id:
        response = make_response({"error": "Scientist not found"}, 404)
        response.headers["Content-Type"] = "application/json"
        return response
    if request.method == 'GET':
        scientists_to_dict = scientists_by_id.to_dict()

        response = make_response(
            scientists_to_dict,
            200
        )
    
        return response
    
    elif request.method == 'DELETE':
        db.session.delete(scientists_by_id)
        db.session.commit()

        response = make_response({}, 204)  # или "" вместо {}
        response.headers["Content-Type"] = "application/json"
        return response

@app.route('/scientists', methods=['POST'])
def post_scientists():
    data = request.get_json()

    try:
        new_scientist = Scientist(
            name=data.get('name'),
            field_of_study=data.get('field_of_study')
        )
        db.session.add(new_scientist)
        db.session.commit()
    except ValueError:
        db.session.rollback()
        response = make_response({"errors": ["validation errors"]}, 400)
        response.headers["Content-Type"] = "application/json"
        return response

    scientist_dict = new_scientist.to_dict()

    response = make_response(scientist_dict, 201)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route('/scientists/<int:id>', methods=['PATCH'])
def patch_scientist(id):
    scientist = Scientist.query.filter_by(id=id).first()

    # ---- invalid ID ----
    if not scientist:
        response = make_response({"error": "Scientist not found"}, 404)
        response.headers["Content-Type"] = "application/json"
        return response

    data = request.get_json()

    try:
        # обновляем только то, что пришло
        if "name" in data:
            scientist.name = data["name"]

        if "field_of_study" in data:
            scientist.field_of_study = data["field_of_study"]

        db.session.commit()

    except ValueError:
        db.session.rollback()
        response = make_response({"errors": ["validation errors"]}, 400)
        response.headers["Content-Type"] = "application/json"
        return response

    # успешно обновлено → вернуть обновлённый scientist + 202
    scientist_dict = scientist.to_dict()
    response = make_response(scientist_dict, 202)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = [
        p.to_dict(only=("id", "name", "distance_from_earth", "nearest_star"))
        for p in Planet.query.all()
    ]

    response = make_response(planets, 200)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route('/missions', methods=['POST'])
def post_mission():
    data = request.get_json()

    try:
        new_mission = Mission(
            name=data.get('name'),
            scientist_id=data.get('scientist_id'),
            planet_id=data.get('planet_id')
        )

        db.session.add(new_mission)
        db.session.commit()

    except ValueError:
        db.session.rollback()
        response = make_response({"errors": ["validation errors"]}, 400)
        response.headers["Content-Type"] = "application/json"
        return response

    mission_dict = new_mission.to_dict()
    response = make_response(mission_dict, 201)
    response.headers["Content-Type"] = "application/json"
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
