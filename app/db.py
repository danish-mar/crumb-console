import mysql.connector
from flask import current_app, g
from flask_pymongo import PyMongo


def get_mongo_db():
    if 'mongo_db' not in g:
        mongo = PyMongo(app=current_app, uri=current_app.config['MONGO_URI'])
        g.mongo_db = mongo.db
    return g.mongo_db


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['SERVER'],
            port=current_app.config['PORT'],
            database=current_app.config['DATABASE'],
            user=current_app.config['USERNAME'],
            password=current_app.config['PASSWORD']
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def close_mongo_db(e=None):
    mongo_db = g.pop('mongo_db', None)
    if mongo_db is not None:
        print("Closing mongo connection")
