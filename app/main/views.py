from flask import render_template, session, redirect, url_for, current_app,jsonify,request,send_from_directory,Response
from . import main
from ..models import *
import json
import mimetypes
from werkzeug import secure_filename
import os
import uuid
from functools import wraps
from .. import app,login_manager
from ..api import User
from flask.ext.login import ( current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUserMixin,
                            confirm_login, fresh_login_required)

ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join("/data", 'files')

def json_response(f):
    @wraps(f)

    def wrap(*args,**kwargs):
        return Response(response=f(*args,**kwargs),
                    status=200,
                    mimetype="application/json")
    return wrap

# def login_required(f):
#     @wraps(f)

#     def wrap(*args,**kwargs):
#         if 'logged_in' in session:
#             return f(*args,**kwargs)
#         else:
#             return json.dumps({'status':0,'error':'User not logged in Oopsey'})
#     return wrap


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@main.route('/upload', methods=['GET', 'POST'])
def upload():
    try:
	    if request.method == 'POST':
		file = request.files['file']
		file_obj = Files()
		return json.dumps({'status':1})
		if file and allowed_file(file.filename):
		    user = current_user.get_mongo_doc()
		    uid = str(uuid.uuid4())
		    filename = secure_filename(file.filename)
		    print 'ospath' , os.path
		    file.save(os.path.join(UPLOAD_FOLDER, uid+filename))
		    file_obj.filename = uid+filename
		    file_obj.file_url = os.path.join(UPLOAD_FOLDER, uid+filename)
		    file_obj.user = user
		    file_obj.save()
		    return json.dumps({'status':1})
    except Exception as inst:
        return json.dumps({'status':inst})



@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER,
                               filename)



@main.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return json.dumps({'status':1})



@main.route('/delete', methods=['POST'])
def delete():
    codes = User.objects()
    for code in codes:
        code.delete()
    return json.dumps({'status':1})


@main.route('/dummy', methods=['POST'])
def dummy():
    user = User(username = 'Navin',password = '12345',phone_number = '4234234234')
    user.save()
    return  Response(json.dumps({'status':1}), mimetype='application/json')




@main.route('/login', methods=['POST'])
@json_response
def login():
    if request.method == "POST" and "email" in request.form:
        email = request.form["email"]
        password = request.form["password"]
        userObj = User.User()
        user = userObj.get_by_email_w_password(email)
        if user and user.password == password:
            # session.permanent = True
            # session['user'] = user
            # session['logged_in'] = True
            remember = request.form.get("remember", "no") == "yes"
            if login_user(user, remember=remember):
                user_doc = current_user.get_mongo_doc()
                user_Barcodes = get_all_barcodes(user_doc)
                user_file_count = get_zip_files_count(user_doc)
                return json.dumps({'status':1,
                                    'barcodes':get_all_barcodes(None),
                                    'barcode_count':len(user_Barcodes),
                                    'user_files':user_file_count})

        elif user:
            return json.dumps({'status':0,'error':'incorrect password'})

        else :
            user = User.User(email,password)
            user.save()
            remember = request.form.get("remember", "no") == "yes"
            if login_user(user, remember=remember):
                user_doc = current_user.get_mongo_doc()
                user_Barcodes = get_all_barcodes(user_doc)
                user_file_count = get_zip_files_count(user_doc)
                return json.dumps({'status':1,
                                    'barcodes':get_all_barcodes(None),
                                    'barcode_count':len(user_Barcodes),
                                    'user_files':user_file_count})

    return json.dumps({'status':2})




@main.route('/sync_barcode', methods=['POST'])
@login_required
@json_response
def sync_barcode():
    barcodes_string = request.form['barcodes']
    barcodes = []
    user = current_user.get_mongo_doc()

#    print 'this is the user ', user.username
    try:
        barcodes = json.loads(barcodes_string)
    except ValueError as e :
        print 'ValueErr',
    for code in  barcodes:
        barcode_obj =  Barcode()
        barcode_obj.code  = code['code']
        barcode_obj.user = user
        barcode_obj.save()
    user_Barcodes = get_all_barcodes(user)
    user_file_count = get_zip_files_count(user)
    return json.dumps({'status':1,
                        'barcodes':get_all_barcodes(None),
                        'barcode_count':len(user_Barcodes),
                        'user_files':user_file_count})

@login_manager.unauthorized_handler
def unauthorized_callback():
    return json.dumps({'status':2})

@login_manager.user_loader
def load_user(id):
    if id is None:
        redirect('/login')
    user = User.User()
    user.get_by_id(id)
    if user.is_active():
        return user
    else:
        return None
