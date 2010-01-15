from google.appengine.ext import db

class RFIDMapping(db.Model):
    rfid = db.StringProperty()
    name = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_secret = db.StringProperty()
    # For instance, we may want to reuse a tag and 
    # keep track of the old name for the access log.
    status = db.StringProperty()

class AccessLog(db.Model):
    rfid_id = db.ReferenceProperty(RFIDMapping)
    access_time = db.DateTimeProperty(auto_now = True)
    foursq_status = db.StringProperty()
