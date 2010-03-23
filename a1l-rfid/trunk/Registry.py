import logging
from pprint import PrettyPrinter
import sys
import traceback
from xml.dom.minidom import parseString

from Models import *
import foursquare
from google.appengine.api import memcache
from google.appengine.ext import webapp
from oauth import oauth

#We currently support hmac-sha1 signed requests
#*Application Name:* Alpha One Labs
#RFID<http://foursquare.com/oauth/www.alphaonelabs.com>

# rfid.alphaonelabs.com
#consumer_key = '1TDWB1RAY1FQJT2HVOUZUMHCCYFBJA5EX0Z440OYZIRQTQMP'
#consumer_secret = 'XAV035QZG2DTALIHXQZ4CHRPZC4AJZAUTRRSWUEJQKDUTEN3'

#a1lrfid.appspot.com/got-request-token
consumer_key = 'RTKOC40KGDJLVYQWFWSBFEIC3VGQWCY4EDIG3FI1TJXW3XZG'
consumer_secret = 'OLVWAGXOZSJLZBFWVUDPWOOOOWK2KEVJ55QEKZCBYJK5C0AO'

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
                %(pic)s
                <div id='results'/>
            </body>
        </html>
    """

    picFragment = """
        <div id='pic'>
            <p>Is this you?</p>
            <img src=%(picurl)s />
        </div>
    """

    saved = """
        <html>
            <head>
                <title>All Done!</title>
                <meta http-equiv='refresh' content='5;url=/'></meta>
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

    def access_resource(self, token, secret, method, ** params):
        logging.info('calling ' + method + ' with ' + PrettyPrinter().pformat(params))
        try:
            credentials = foursquare.OAuthCredentials(\
                                                      consumer_key, consumer_secret)
            fs = foursquare.Foursquare(credentials)
            user_token = oauth.OAuthToken(token, secret)
            credentials.set_access_token(user_token)
            resp = fs.call_method(method, ** params)
            logging.debug('returning ' + resp)
            return resp
        except Exception, e:
            # If the request failed, display the something went wrong page
            logging.error("Failed registry request: " + str(e))
            traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], 
                                      sys.exc_info()[2], 5, sys.stderr)
            return None

    def get(self):
        return self.post()

    def post(self):
        logging.getLogger().setLevel(logging.DEBUG)

        # What step are we here with?
        logging.info("request: " + self.request.path)
        try:
            credentials = foursquare.OAuthCredentials(\
                                                      consumer_key, consumer_secret)
            fs = foursquare.Foursquare(credentials)

            if self.request.path == "/register":
                logging.debug("Register entry")
                # Get the temporary auth token
                app_token = fs.request_token()
                auth_url = fs.authorize(app_token)
                if not memcache.set(key='token', value=app_token):
                    raise Exception("Failed to set token in session")
                self.response.out.write(
                                        self.requestAuthorization % {'url': auth_url}
                                        )

            elif self.request.path == '/got-request-token':
                logging.debug("Register with auth token")
                token = memcache.get('token');
                if token is None:
                    raise "No token stored in session"
                # Check the auth token by converting it into a token + secret
                logging.info('* Obtain an access token ...')
                user_token = fs.access_token(token)
                credentials.set_access_token(user_token)
                if not memcache.set(key='token', value=user_token):
                    raise Exception("Failed to set token in session")
                logging.info('GOT')
                logging.info('key: %s' % str(user_token.key))
                logging.info('secret: %s' % str(user_token.secret))
                if not memcache.set('saveInsteadOfCheckin', True):
                    raise Exception("Failed to set save flag")
                try:
                    respstr = fs.user()
                    resp = parseString(respstr)
                    logging.debug('resp: ' + str(respstr))
                    firstnameNode = resp.getElementsByTagName('firstname')[0]
                    firstname = firstnameNode.firstChild.data
                    lastnameNode = resp.getElementsByTagName('lastname')[0]
                    lastname = lastnameNode.firstChild.data
                    picNode = resp.getElementsByTagName('photo')[0]
                    picurl = picNode.firstChild.data
                    pic = self.picFragment % {'picurl': picurl}
                except:
                    traceback.print_exception(sys.exc_info()[0], 
                                              sys.exc_info()[1],
                                              sys.exc_info()[2], 5, sys.stderr)
                    firstname = 'First'
                    lastname = 'last'
                    pic = ''

                self.response.out.write(
                                        self.gotAuthorization % {
                                        'firstname': firstname, 'lastname': lastname,
                                        'pic': pic
                                        }
                                        )
            elif self.request.path == '/save-request-token':
                logging.debug("Save token data")
                memcache.delete("saveInsteadOfCheckin")
                token = memcache.get('token');
                if token is None:
                    raise "No token stored in session"
                # Store those in the database and let them know we're good
                user_rec = RFIDMapping()
                user_rec.rfid = self.request.get("tag_id")
                user_rec.name = self.request.get("first_name") + \
                    " " + self.request.get("last_name")
                user_rec.foursq_status = "None"
                user_rec.oauth_token = token.key
                user_rec.oauth_secret = token.secret
    
                logging.debug("saving user data")
                # Now save the data
                db.put(user_rec)
                self.response.out.write(self.saved)
            else:
                raise Exception("Unknown request: " + self.request.path)

        except Exception, e:
            # If the request failed, display the something went wrong page
            self.response.out.write(self.authFailed)
            logging.error("Failed registry request: " + str(e))
            traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], 
                                      sys.exc_info()[2], 5, sys.stderr)
            return

