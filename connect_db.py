import psycopg2
import datetime
# from account import user_login, user_pass
from config import PG_LOGIN, PG_PASSWORD

def add_to_base(dict_my):
    
    # id = dict_my['Id']
    sender = dict_my['Sender']
    email = dict_my['Email']
    send_date = dict_my['Date']
    recipient = dict_my['Recipient']
    subscription = dict_my['Subscription']

    fmt = "%Y %m %d"
    send_date = datetime.datetime.strptime(send_date, fmt)

    try:
        conn = psycopg2.connect(
            user = PG_LOGIN,
            password = PG_PASSWORD,                           
            database = 'antipodpiska',
            host = 'db',                                            # Production
            # host = 'localhost',                                   # Development
            port = 5432,
        )
    except Exception as ex:
        print(' /// ----- I am unable to connect to the database ----- ///', ex)
        raise ex

    cur = conn.cursor()


# GETTING DATA FROM DB
    
    # postgreSQL_select_Query = "SELECT * FROM public.anti;"
    # cur.execute(postgreSQL_select_Query)

    # print("Selecting rows from mobile table using cursor.fetchall")
    # mobile_records = cur.fetchall()
    # print('=============================================================')
    # print(mobile_records)
    # print(type(mobile_records))
    # print('=============================================================')




    cur.execute( # 'cur' object calls the 'execute' method 
        """INSERT INTO public.anti(
            sender, email, send_date, recipient, subscription) VALUES (
                %(sender)s,
                %(email)s,
                %(send_date)s,
                %(recipient)s,
                %(subscription)s
            )""",
            {
            'sender' : sender,
            'email': email,
            'send_date' : send_date,
            'recipient' : recipient,
            'subscription' : subscription
            }
    )
    conn.commit()

    cur.close()
    conn.close()
    print('Done ok. 200')


if __name__ == '__main__':
    # add_to_base(id, sender, email, send_date)
    add_to_base(dict_my)