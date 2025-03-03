import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
# =================================================================================
from flask_cors import CORS #comment this on deployment
# =================================================================================


import config as config
from app_yandex import get_data

# # __init__.py
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(APP_DIR, 'static_html/js/') # Where your webpack build output folder is
TEMPLATE_FOLDER = os.path.join(APP_DIR, 'static_html/') # Where your index.html file is located


# from models import Sender



# BASE Connection
try:
    # engine = create_engine('postgresql://username:password@localhost:5432/mydatabase')
    engine = create_engine(
        'postgresql://postgres:258963@localhost:5432/antipodpiska')
    print('=================================================================================')
    print(engine)
    print('=================================================================================')
except:
    print("Can't create 'engine")




app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
# app = Flask(__name__)
# =================================================================================
CORS(app) #comment this on deployment
# =================================================================================
app.config.from_object(config)
db = SQLAlchemy(app)

@app.route('/', methods=['GET'])
def execute_SQL():
    print('=============================================================')
    print('execute_SQLexecute_SQLexecute_SQL')
    print('=============================================================')
    # We use 'sqlalchemy' to get data from DB
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * from public.anti;"))
        # result = connection.execute(text("SELECT sender from public.anti;"))
        # print(type(result))
        # print(result)
        print('=============================================================')
        result_dict = {}
        c = 1
        for row in result:
            # print(row)
            # print("sender:", row['sender'])
            dict_key = {}
            dict_key["sender"] = row['email']
            dict_key["Subscription"] = row['subscription']
            c += 1
            result_dict[c] = dict_key
   
    # return jsonify({
    #      'sender': [p.to_dict() for p in senders],
    #  })
        # print(result_dict)
    # return jsonify(result_dict)
    return render_template('index.html')

@app.route('/account', methods=['POST'])
def post():
    data = request.get_json()
    print(data)
    mail_service = data['mail_service']
    login = data['login']
    password = data['password']
    print('-------------------------------')
    print(mail_service, login, password)

    
    # from sqlalchemy_engine.account import mail_service, login, password
    get_data(mail_service, login, password)
    try:
        # user = User(**data)
        # user.save_to_db()
        return {'status': 'ok'}, 200
    except:
        return {'status': 'fail'}, 400




# def post():
#     mail_service = request.get_json()
#     login = request.get_json()
#     password = request.get_json()
#     print(mail_service)
#     try:
#         # user = User(**data)
#         # user.save_to_db()
#         return {'status': 'ok'}, 200
#     except:
#         return {'status': 'fail'}, 400



# def upgrade_db():
#     print('Creating sender')
#     data = {}

    # db.session.add(data)
    # db.session.commit() 

if __name__ == '__main__':
    # from models import *
    # db.create_all()

    # senders = Sender.query.all()
    # print(list(map(str, senders)))

    app.run()


# I need to ensure that databese work correct, at first!!!!
# Then connect mail reader with with this app.