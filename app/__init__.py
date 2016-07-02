#!/usr/lib/python2.7
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask.ext.login import LoginManager


app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB':'IBOTAPP'}
db = MongoEngine(app)

app.config.from_object('config')
app.config["SECRET_KEY"] = "KeepThisS3cr3t"
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip'])


login_manager = LoginManager()
login_manager.init_app(app)
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)
