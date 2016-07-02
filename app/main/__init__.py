#!/usr/lib/python2.7
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
