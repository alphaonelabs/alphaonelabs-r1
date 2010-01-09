from google.appengine.api import db

class RFIDMapping(db.Model):
    rfid = db.StringProperty()
    name = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_secret = db.StringProperty()

class AccessLog(db.Model):
    rfid_id = db.ReferenceProperty(RFIDMapping)
    access_time = db.DateTimeProperty()
