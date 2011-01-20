from google.appengine.ext import db

class RFIDMapping(db.Model):
    rfid = db.StringProperty()
    name = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_secret = db.StringProperty()
    status = db.StringProperty()

class AccessLog(db.Model):
    rfid_record = db.ReferenceProperty(RFIDMapping)
    rfid_id = db.StringProperty()
    access_time = db.DateTimeProperty(auto_now=True)
    foursq_status = db.StringProperty()
