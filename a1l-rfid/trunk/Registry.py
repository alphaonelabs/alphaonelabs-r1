from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from oauth import oauth
from simpleOauthClient import SimpleOauthClient
import os
from google.appengine.ext.webapp import template
import httplib
import time
import logging

Request_Token_URL='http://foursquare.com/oauth/request_token'
Access_Token_URL='http://foursquare.com/oauth/access_token'
Authorize_URL='http://foursquare.com/oauth/authorize'
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
                <meta http-equiv='refresh' content='0;href=%(url)s'></meta>
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
            </head>
            <body>
                <h1>Scan RFID tag</h1>
                <p>You can always log in to foursquare to revoke or change these
                credentials.</p>
                <p>Now let's scan your tag, so you won't have to do this agan</p>
                <form method='POST'>
                    <table border='0'>
                    <tr><td>First Name: </td>
                     <td><input type='text' name='first_name' value='%(firstname)s'/></td>
                     </tr>
                    <tr><td>Last Name:</td>
                     <td><input type='text' name='last_name' value='%(lastname)s'/></td>
                     </tr>
                    <tr><td>Tag ID:</td><td><input type='text' name='tag_id' value=''/></td>
                    <tr><td colspan='2'><input type='submit' name='save' value='Save'/></td>
                    </tr>
                    </table>
                    <input type='hidden' name='token' value='%(token)s'/>
                    <input type='hidden' name='secret' value='%(secret)s'/>
                </form>
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
                <meta http-equiv='refresh' content='0;href=%s'></meta>
            </head>
            <body>
                <h1><font color='red'>Something went wrong!</font></h1>
                We couldn't process your authorization into 
                Foursquare.  Please try again later.
            </body>
        </html>
    """

    def get(self):
        client = SimpleOAuthClient('foursquare.com', 80,
                    Request_Token_URL, Access_Token_URL, Authorize_URL)
        consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        # What step are we here with?
        # TODO: This test won't work if auth fails
        if self.request.get("oauth_token") == "":
            # Get the temporary auth token
            oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, 
                    callback=Callback_URL, http_url=client.request_token_url)
            oauth_request.sign_request(signature_method_hmac_sha1, consumer, None)
            logging.debug('REQUEST (via headers)')
            logging.debug('parameters: %s' % str(oauth_request.parameters))
            token = client.fetch_request_token(oauth_request)
            logging.debug('GOT')
            logging.debug('key: %s' % str(token.key))
            logging.debug('secret: %s' % str(token.secret))
            logging.debug('callback confirmed? %s' % str(token.callback_confirmed))

            # If the request failed, display the something went wrong page

            # Construct the request URL
            oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=client.authorization_url)
            logging.debug('REQUEST (via url query string)')
            logging.debug('parameters: %s' % str(oauth_request.parameters))

            self.response.out.write(
                self.requestAuthorization % { 'url': oauth_request.to_url() }
            )
        else:
            # Check the auth token by converting it into a token + secret
            logging.debug('* Obtain an access token ...')
            oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                consumer, token=token, verifier=verifier, 
                http_url=client.access_token_url)
            oauth_request.sign_request(signature_method_plaintext, consumer, token)
            logging.debug('REQUEST (via headers)')
            logging.debug('parameters: %s' % str(oauth_request.parameters))
            token = client.fetch_access_token(oauth_request)
            logging.debug('GOT')
            logging.debug('key: %s' % str(token.key))
            logging.debug('secret: %s' % str(token.secret))

    def post(self):
            # Store those in the database and let them know we're good
            user_rec = RFIDMapping()
            user_rec.rfid = self.request.get("tag_id")
            user_rec.name = self.request.get("first_name") + " " + self.request.get("last_name")
            user_rec.foursq_status = "None"

            # Now save the data
            try:
                db.put(user_rec)
                self.response.out.write(self.saved)
            except:
                self.response.out.write(self.authFailed)
            
