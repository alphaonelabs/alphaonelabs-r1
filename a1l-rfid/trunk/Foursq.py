from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.memcache import Client
from google.appengine.ext import db
from simpleOauthClient import SimpleOAuthClient
import logging
from Models import * 

Request_Token_URL='http://foursquare.com/oauth/request_token'
Access_Token_URL='http://foursquare.com/oauth/access_token'
Authorize_URL='http://foursquare.com/oauth/authorize'
Callback_URL='/got-request-token'

class Foursq(webapp.RequestHandler):
    venue_id = 1111

    def get(self):
        client = SimpleOAuthClient('foursquare.com', 80,
                    Request_Token_URL, Access_Token_URL, Authorize_URL)
        consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        if Client.get('saveInsteadOfCheckin') is not None and \
                Client.get('savedId') is None:
            Client.set('savedId', self.request.get('scanned_id'))
        else:
            # Add a log entry for the scan
            entry = AccessLog()
            entry.rfid_id = self.request.get('scanned_id')
            entry.foursq_status = "unknown"
            try:
                db.put(entry)

                # Find the scanned ID in the database
                query = db.GqlQuery("select * from RFIDMapping where rfid = :1",
                    self.request.get('scanned_id'))
                mapping = query.get()
                # Use the stored token and secret to perform a checkin
                rc = client.access_resource({'vid': venue_id},'/v1/checkin')

                # update the log entry's status
                entry.foursq_status = "checked_in"
                db.put(entry)

            except Exception:
                log.error(e.str())
