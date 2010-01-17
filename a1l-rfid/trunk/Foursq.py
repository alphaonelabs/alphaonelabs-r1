from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache 
from google.appengine.ext import db
import logging
from Models import * 
import Registry
import traceback
import sys

class Foursq(webapp.RequestHandler):
    venue_id = 1111

    def get(self):
        try:
            if self.request.path == '/rfid':
                if memcache.get('saveInsteadOfCheckin') is not None and \
                        Client.get('savedId') is None:
                    memcache.set(key='savedId', value=self.request.get('scanned_id'))
                else:
                    # Add a log entry for the scan
                    entry = AccessLog()
                    entry.rfid_id = self.request.get('scanned_id')
                    entry.foursq_status = "unknown"
                    db.put(entry)

                    # Find the scanned ID in the database
                    query = db.GqlQuery("select * from RFIDMapping where rfid = :1",
                        self.request.get('scanned_id'))
                    mapping = query.get()
                    # Use the stored token and secret to perform a checkin
                    client = Registry()
                    rc = client.access_resource(mapping, {'vid': venue_id},'/v1/checkin')

                    # update the log entry's status
                    entry.foursq_status = "checked_in"
                    db.put(entry)
            elif self.request.path == '/last-rfid':
                self.response.out.write(memcache.get('savedId'))
                return
            else:
                raise Exception("Unknown request: "+request.path)

        except Exception,  e:
                logging.error(str(e))
                traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1],
                                          sys.exc_info()[2], 5, sys.stderr)

