from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from oauth import oauth
from simpleOauthClient import SimpleOAuthClient
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import httplib
import time
import logging
import traceback
import sys
from Models import *

Request_Token_URL='http://foursquare.com/oauth/request_token'
Access_Token_URL='http://foursquare.com/oauth/access_token'
Authorize_URL='http://foursquare.com/oauth/authorize'
API_URL='http://api.foursquare.com'
Callback_URL='/got-request-token'

#We currently support hmac-sha1 signed requests
#*Application Name:* Alpha One Labs
#RFID<http://foursquare.com/oauth/www.alphaonelabs.com>

consumer_key = '1TDWB1RAY1FQJT2HVOUZUMHCCYFBJA5EX0Z440OYZIRQTQMP'
consumer_secret = 'XAV035QZG2DTALIHXQZ4CHRPZC4AJZAUTRRSWUEJQKDUTEN3'

class Registration(webapp.RequestHandler):
    requestAuthorization = """
        <html>
            <head>
                <title>Getting Authorization from Foursquare</title>
                <meta http-equiv='refresh' content='0;url=%(url)s'></meta>
            </head>
            <body>
                <h1>Hang on while we redirect you to foursquare</h1>
                Please click <a href='%(url)s'>here</a> if you are not automatically
                    redirected...
            </body>
        </html>
    """

    gotAuthorization = """
        <html>
            <head>
                <title>Details</title>
                <script type="text/javascript" src="authpage.js">
                </script>
            </head>
            <body onload="wait_for_tag()">
                <h1>Scan RFID tag</h1>
                <p>You can always log in to foursquare to revoke or change these
                credentials.</p>
                <p>Now let's scan your tag, so you won't have to do this again</p>
                <form method='POST' action='/save-request-token'>
                    <table border='0'>
                    <tr><td>First Name: </td>
                     <td><input type='text' name='first_name' value='%(firstname)s'/></td>
                     </tr>
                     <tr><td>Last Name:</td>
                     <td><input type='text' name='last_name' value='%(lastname)s'/></td>
                     </tr>
                    <tr><td>Tag ID:</td><td><input type='text' id='tag_id' name='tag_id' value=''/></td>
                    <tr><td colspan='2'><input type='submit' name='save' value='Save'/></td>
                    </tr>
                    </table>
                </form>
                <div id='results'/>
            </body>
        </html>
    """

    saved = """
        <html>
            <head>
                <title>All Done!</title>
            </head>
            <body>
                <h1><font color='green'>All Done</font></h1>
                <p>You're all saved in the database.  Go ahead and check in for
                the first time!</p>
                <p>Thanks for joining</p>
            </body>
        </html>
    """

    authFailed = """
        <html>
            <head>
                <title>Something went wrong!</title>
            </head>
            <body>
                <h1><font color='red'>Something went wrong!</font></h1>
                We couldn't process your authorization into 
                Foursquare.  Please try again later.
            </body>
        </html>
    """

    def get(self):
        return self.post()

    def access_resource(self, mapping, params, url):
        client = SimpleOAuthClient('foursquare.com', 80,
                    Request_Token_URL, Access_Token_URL, Authorize_URL)
        consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        token = oauth.OAuthToken(mapping.oauth_token, mapping.oauth_secret)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            consumer, token=token, verifier=None, 
            http_url=API_Url)
        oauth_request.sign_request(signature_method_hmac_sha1, 
            consumer, token)
        for k in params.keys():
            oauth_request.set_parameter(k, params[k])
        return client.access_resource(oauth_request, url)

    def post(self):
        logging.getLogger().setLevel(logging.DEBUG)
        client = SimpleOAuthClient('foursquare.com', 80,
                    Request_Token_URL, Access_Token_URL, Authorize_URL)
        consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        # What step are we here with?
        logging.info("request: "+self.request.path)
        # TODO: This test won't work if auth fails
        try:
            if self.request.path == "/register":
                logging.debug("Register entry")
                # Get the temporary auth token
                oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                    consumer, callback=Callback_URL, 
                    http_url=client.request_token_url)
                oauth_request.sign_request(signature_method_hmac_sha1, 
                                        consumer, None)
                logging.info('REQUEST (via headers)')
                logging.info('parameters: %s' % str(oauth_request.parameters))
                token = client.fetch_request_token(oauth_request)
                logging.info('GOT')
                logging.info('key: %s' % str(token.key))
                logging.info('secret: %s' % str(token.secret))
                logging.info('callback confirmed? %s' 
                    % str(token.callback_confirmed))
                if not memcache.set(key='token',value=token):
                    raise Exception("Failed to set token in session")
                # Construct the request URL
                oauth_request = oauth.OAuthRequest.from_token_and_callback(
                    token=token, http_url=client.authorization_url)
                logging.info('REQUEST (via url query string)')
                logging.info('parameters: %s' % str(oauth_request.parameters))
                logging.debug("URL "+oauth_request.to_url())

                self.response.out.write(
                    self.requestAuthorization % { 'url': oauth_request.to_url() }
                )
            elif self.request.path == '/got-request-token':
                logging.debug("Register with auth token")
                token = memcache.get('token');
                if token is None:
                    raise "No token stored in session"
                # Check the auth token by converting it into a token + secret
                logging.info('* Obtain an access token ...')
                oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                    consumer, token=token, verifier=None, 
                    http_url=client.access_token_url)
                oauth_request.sign_request(signature_method_hmac_sha1, 
                    consumer, token)
                logging.info('REQUEST (via headers)')
                logging.info('parameters: %s' % str(oauth_request.parameters))
                token = client.fetch_access_token(oauth_request)
                logging.info('GOT')
                logging.info('key: %s' % str(token.key))
                logging.info('secret: %s' % str(token.secret))
                if not memcache.set('saveInsteadOfCheckin', True):
                    raise Exception("Failed to set save flag")
                self.response.out.write(
                    self.gotAuthorization % {
                        'firstname': 'First', 'lastname': 'Last'
                    }
                )
            elif self.request.path == '/save-request-token':
                logging.debug("Save token data")
                token = memcache.get('token');
                if token is None:
                    raise "No token stored in session"
                # Store those in the database and let them know we're good
                user_rec = RFIDMapping()
                user_rec.rfid = self.request.get("tag_id")
                user_rec.name = self.request.get("first_name") + " " + self.request.get("last_name")
                user_rec.foursq_status = "None"
                user_rec.oauth_token = token.key
                user_rec.oauth_secret = token.secret
    
                logging.debug("saving user data")
                # Now save the data
                db.put(user_rec)
                self.response.out.write(self.saved)
            else:
                raise Exception("Unknown request: "+self.request.path)

        except Exception, e:
            # If the request failed, display the something went wrong page
            self.response.out.write(self.authFailed)
            logging.error("Failed registry request: "+str(e))
            traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], 
                                      sys.exc_info()[2], 5, sys.stderr)
            return

