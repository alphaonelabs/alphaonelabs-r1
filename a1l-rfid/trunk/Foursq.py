from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache 
from google.appengine.ext import db
import logging
from Models import * 
from Registry import Registration
import traceback
import sys

class Foursq(webapp.RequestHandler):
    venue_id = 87607

    def get(self):
        try:
            if self.request.path == '/rfid':
                if memcache.get('saveInsteadOfCheckin') is not None and \
                        memcache.get('savedId') is None:
                    if not memcache.set('savedId', self.request.get('scanned_id')):
                        raise Exception("Failed to save scanned id")
                else:
                    # Add a log entry for the scan
                    if self.request.get('scanned_id') is None:
                        raise Exception("No scanned ID!?")
                    entry = AccessLog()
                    entry.rfid_id = self.request.get('scanned_id')
                    entry.foursq_status = "initial scan"
                    db.put(entry)

                    # Find the scanned ID in the database
                    query = db.GqlQuery("select * from RFIDMapping where rfid = :1",
                        self.request.get('scanned_id'))
                    mapping = query.get()
                    entry.rfid_record = mapping
                    db.put(entry)

                    # Use the stored token and secret to perform a checkin
                    logging.getLogger().setLevel(logging.DEBUG)
                    logging.debug("token "+mapping.oauth_token)
                    logging.debug("secret "+mapping.oauth_secret)
                    client = Registration()
                    rc = client.access_resource(
                        mapping.oauth_token, mapping.oauth_secret, 
                        '/v1/checkin', "POST", vid=self.venue_id)

                    # update the log entry's status
                    entry.foursq_status = "checked_in"
                    db.put(entry)
            elif self.request.path == '/last-rfid':
                id = memcache.get('savedId')
                if id is not None:
                    self.response.out.write(id+"\n")
                    memcache.delete('savedId')
                return
            else:
                raise Exception("Unknown request: "+request.path)

        except Exception,  e:
                logging.error(str(e))
                traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1],
                                          sys.exc_info()[2], 5, sys.stderr)

