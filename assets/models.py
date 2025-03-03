from app import db



class Antipodpiska(db.Model):
    send_date = db.Column(db.DateTime())
    email = db.Column(db.String(255))
    sender = db.Column(db.String(255))
    subscription = db.Column(db.String(255))
    recipient = db.Column(db.String(255))


    def __init__(self,
        send_date,
        email,
        sender,
        subscription,
        recipient) -> None:
        self.send_date = send_date
        self.email = email
        self.sender = sender
        self.subscription = subscription
        self.recipient = recipient

    def __str__(self):
        return '<Message {}, {}, {}, {}, {}>'.format(self.send_date, self.email, self.sender, self.subscription, self.recipient)



    @staticmethod
    def get_latest_sender():
        senders_to_list = {}

        result = db.engine.execute(
            """ SELECT t.send_date, t.email, t.sender, t.subscription, t.recipient
                from anti t """) 

        print(next(result))


        for t in result:
            if t.sender in senders_to_list:
                senders_to_list.get(t.sender).append(dict(t))
            else:
                senders_to_list[t.sender] = [dict(t)]

        print('-------------------------------------------------------')
        print(senders_to_list)


        return senders_to_list