# -*- coding: utf-8 -*- 

from collections import Counter
import csv
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, request, g, jsonify, abort, make_response, redirect, url_for, send_from_directory, render_template, flash, Response, session
import pandas as pd
import pytz
import json
import urllib
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, UserMixin, login_required,login_user, current_user, logout_user
from wtforms import Form, BooleanField, StringField, validators
import numpy as np





app = Flask(__name__)
CORS(app)

from globalfunc import * 
import citibikeapp.assignTaskPy
import citibikeapp.dashboardPy
import citibikeapp.iosresponsePy
import citibikeapp.manageTablePy
import citibikeapp.greedyPy
import citibikeapp.mapPy
import citibikeapp.searchTaskPy
import citibikeapp.addEntryPy
import citibikeapp.breakPy
import citibikeapp.shiftPy

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'super secret key'

@app.route('/')
def hello_world():
    joke = "Q: What do you get if you cross a bike and a flower? \n A: Bicycle petals! \n "
    sourceurl = 'http://www.jokes4us.com/sportsjokes/cyclingjokes.html'
    return joke+sourceurl

@app.route('/index')
@login_required
def index():
    return render_template("index.html",
                           title='Index')

DATABASE = '/var/www/html/citibikeapp/citibikeapp/citibike_change.db'

app.config.from_object(__name__)

########################################## Login #################################################################

class User(UserMixin):

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls,id):
        result = execute_query("""SELECT * FROM Users Where username = ?
         """,
         [id])
        try:
            user = User(id,result[0][1])
        except Exception as e:
            return None
        
        return user

def validate_user(username,psw):
        result = execute_query("""SELECT * FROM Users Where username = ? and psw = ?
         """,
         [username, psw])
        if len(result)!= 0:
            return True
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login')
def login():
    message = 'Wrong Username or Password'
    # if login_attempt!=0:
    #     message = "Wrong Username or password"
    return render_template('login.html', message = message)

@app.route('/login2', methods=['GET', 'POST'])
def login2():
    print "logging in"
    username = request.form['username']
    password = request.form['password']
    print "get all attributes"

    if validate_user(username,password):
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User(username,password)
        login_user(user,remember=True)

        flash('Logged in successfully.')

        # # next = flask.request.args.get('next')
        # # # is_safe_url should check if the url is safe for redirects.
        # # # See http://flask.pocoo.org/snippets/62/ for an example.
        # # if not is_safe_url(next):
        # #     return flask.abort(400)

        # return flask.redirect(next or flask.url_for('index'))
        return redirect('/dashboard')
    print "did not validate"
    return redirect('/login')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')


############################ Error Handler ############################################################################################

@app.errorhandler(400)#no request form name
def not_complete(error):
    print "400 error"
    #return make_response(jsonify({'error' : 'request not complete'}), 400)
    return "Oops, something is wrong. Did you forget an input? 400 Error"

@app.errorhandler(404)
def not_found(error):
    print "404 error"
    #return make_response(jsonify({'error': 'Not found'}), 404)
    return "Oops, something is wrong. Did you put in the wrong url? 404 Error"
    

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('login.html', message = "Please Login")




if __name__ == '__main__':
    app.run()
