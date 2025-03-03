import psycopg2.extras
from datetime import timedelta


import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
# =================================================================================
# from flask_cors import CORS #comment this on deployment
# =================================================================================


import config as config
from config import PG_LOGIN, PG_PASSWORD
from app_yandex import get_data

# # __init__.py
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(APP_DIR, 'static_html/js/') # Where your webpack build output folder is
TEMPLATE_FOLDER = os.path.join(APP_DIR, 'static_html/') # Where your index.html file is located


# from models import Sender



# BASE Connection
# try:
#     engine = create_engine(
#         f'postgresql://{PG_LOGIN}:{PG_PASSWORD}@db:5432/antipodpiska')                    # Production
#         # f'postgresql://{PG_LOGIN}:{PG_PASSWORD}@localhost:5432/antipodpiska')           # Development
#     print('engine: ', engine)
# except:
#     print("Can't create 'engine")




app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
# app = Flask(__name__)
# =================================================================================
# CORS(app) #comment this on deployment
# =================================================================================
app.config.from_object(config)
db = SQLAlchemy(app)
# from models import *





@app.route('/', methods=['GET'])
def index():
    
    # We use 'sqlalchemy' to get data from DB
    # with engine.connect() as connection:
    #     result = connection.execute(text("SELECT * from public.anti;"))
    #     # result = connection.execute(text("SELECT sender from public.anti;"))
    #     result_dict = {}
    #     c = 1
    #     for row in result:
    #         # print(row)
    #         # print("sender:", row['sender'])
    #         dict_key = {}
    #         dict_key["sender"] = row['email']
    #         dict_key["Subscription"] = row['subscription']
    #         c += 1
    #         result_dict[c] = dict_key
   
    # return jsonify({
    #      'sender': [p.to_dict() for p in senders],
    #  })
        # print(result_dict)
    # return jsonify(result_dict)
    return render_template('index.html')

@app.route('/account', methods=['POST'])
def post():
    data = request.get_json()
    mail_service = data['mail_service']
    login = data['login']
    password = data['password']
    keys_list = data['keyWords']
    keys_list = keys_list.split()

    
    # from sqlalchemy_engine.account import mail_service, login, password
    get_data(mail_service, login, password, keys_list)                      # Push this data to app_yandex

    

    try:
        # user = User(**data)
        # user.save_to_db()
        return {'status': 'ok'}, 200
    except:
        return {'status': 'fail'}, 400


# @app.route('/check', methods=['GET'])
# def execute_SQL():
    # We use 'sqlalchemy' to get data from DB
    # with engine.connect() as connection:
    #     connection.execute(text("DELETE FROM public.anti WHERE ctid NOT IN (SELECT max(ctid) FROM public.anti GROUP BY public.anti.*);"))
    #     result = connection.execute(text("SELECT * from public.anti;"))

        # result = connection.execute(text("SELECT sender from public.anti;"))
        
        #  USE THIS OR ARRAY
        # ------------ Logic for Dict ---------------
        # result_dict = {}
        # c = 0
        # for row in result:
        #     dict_key = {}
        #     dict_key["sender"] = row['email']
        #     dict_key["Subscription"] = row['subscription']
        #     c += 1
        #     result_dict[c] = dict_key
    # return result_dict
        
        #  USE THIS OR DICT
        # --------------- Logic for Array ----------------
    #     result_list = []
    #     for row in result:
    #         dict_key = {}
    #         dict_key["Send Date"] = row['send_date']
    #         dict_key["sender"] = row['email']
    #         dict_key["Subscription"] = row['subscription']
    #         # dict_key["Recipient"] = row['recipient']
    #         result_list.append(dict_key)
       
    # return jsonify(result_list)


TWONY_TWO_DAYS = timedelta(22)

@app.route('/senders', methods=['GET'])
def get_latest_sender():

        user = request.args.get('login')

        try:
            conn = psycopg2.connect(
                user = PG_LOGIN,
                password = PG_PASSWORD,                           
                database = 'antipodpiska',
                host = 'db',                                # Production
                # host = 'localhost',                       # Development
                port = 5432,
            )
        except Exception as ex:
            print(' /// ----- I am unable to connect to the database ----- ///', ex)
            raise ex

       
        # cur = conn.cursor()
        cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        # cur.execute('DELETE FROM public.anti;')
        
        # This sql delete all equal rows!
        cur.execute("DELETE FROM public.anti WHERE ctid NOT IN (SELECT max(ctid) FROM public.anti GROUP BY public.anti.*);")
        cur.execute(
        f"""
        SELECT send_date, email, subscription, recipient from public.anti WHERE subscription > 0 AND recipient='{user}';
        """
        )
        result = cur.fetchall()

        result_list_total_data : list = []
        result_list : list = []
        result_list_periods : list = []
        for row in result:
            dict_key = {}
            dict_key["Send Date"] = row['send_date']
            dict_key["sender"] = row["email"]
            dict_key["Subscription"] = row["subscription"]
            dict_key["Recipient"] = row['recipient']
            result_list.append(dict_key)


        #   =============================================
        #   ====== Объеденяем даты по получателям =======
        #   =============================================
        # Словарь с отправителями из БД
        senders_periods_dict : dict = {}
   
        # Каждый словарь массива отправителей
        
        for each_sender in range(len(result_list)):
            # print(result_list[each_sender])
            senders_periods_dict[result_list[each_sender]['sender']] = [[]]

        # Если ключ в senders_periods_dict равен значению sender в dict_key,
        # то поместить значение даты в массив значений senders_periods_dict
        for key, dates in sorted(senders_periods_dict.items()):
            for each_dict in range(len(result_list)):
                for each_sender in dates:
                    if key == result_list[each_dict]['sender']:
                        each_sender.append(result_list[each_dict]['Send Date'])

     
        # print('===================')
        # Проверка на периодичность
        quantity_of_periods = 0
        for k,v in senders_periods_dict.items():
            list_of_dates = v[0]
            
            if len((v[0])) > 1:
                if list_of_dates[0] - list_of_dates[1] > TWONY_TWO_DAYS:
                    periods_dict_key = {}
                    periods_dict_key['Sender of Subscription'] = k
                    periods_dict_key['Last Send Date'] = list_of_dates[0]
                    periods_dict_key['Periods'] = len(list_of_dates)
                    quantity_of_periods += 1
                    result_list_periods.append(periods_dict_key)
                else:
                    pass
    
        
        #   ========================================
        #   ====== Даты по получателям конец =======
        #   ========================================

        result_list_total_data.append(result_list)
        result_list_total_data.append(result_list_periods)





        cur.close()
        conn.close()

        # return jsonify(result_list)
        return jsonify(result_list_total_data)



if __name__ == '__main__':
    # from models import *
    # db.create_all()

    # senders = Sender.query.all()
    # print(list(map(str, senders)))

    app.run(port=5000, host='0.0.0.0')
    # app.run(host='34.141.12.119', port=5000 )

