from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from oauth.oauth import oauth

Request_Token_URL='http://foursquare.com/oauth/request_token'
Access_Token_URL='http://foursquare.com/oauth/access_token'
Authorize_URL='http://foursquare.com/oauth/authorize'

#We currently support hmac-sha1 signed requests
#*Application Name:* Alpha One Labs
#RFID<http://foursquare.com/oauth/www.alphaonelabs.com>
#*Callback URL:* http://rfid.alphaonelabs.com

consumer_key = '1TDWB1RAY1FQJT2HVOUZUMHCCYFBJA5EX0Z440OYZIRQTQMP'
consumer_secret = 'XAV035QZG2DTALIHXQZ4CHRPZC4AJZAUTRRSWUEJQKDUTEN3'

class Registration(webapp.RequestHandler):
    self.requestAuthorization = """
        <html>
            <head>
                <title>Getting Authorization from Foursquare</title>
                <meta http-equiv='refresh' content='0;href=%s'></meta>
            </head>
            <body>
                <h1>Hang on while we redirect you to foursquare</h1>
                Please click <a href='%s'>here</a> if you are not automatically
                    redirected...
            </body>
        </html>
    """

    self.gotAuthorization = """
        <html>
            <head>
                <title>Cool, you're done!</title>
            </head>
            <body>
                <h1>You're all done!</h1>
                You can always log in to foursquare to revoke or change these
                credentials.
            </body>
        </html>
    """

    self.authFailed = """
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
        oauth auth = oauth()
        # Did we get here to register, or with a response?
        if (request.get("oauth_token") == "":
            # Get the temporary auth token
            # Construct the request URL
            self.response.out.write(
            )
        else:
            # Check the auth token by converting it into a token + secret
            # Store those in the database and let them know we're good
