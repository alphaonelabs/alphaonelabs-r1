from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from oauth.oauth import oauth
import httlib
import time

Request_Token_URL='http://foursquare.com/oauth/request_token'
Access_Token_URL='http://foursquare.com/oauth/access_token'
Authorize_URL='http://foursquare.com/oauth/authorize'

#We currently support hmac-sha1 signed requests
#*Application Name:* Alpha One Labs
#RFID<http://foursquare.com/oauth/www.alphaonelabs.com>
Callback_URL=/got-request-token

consumer_key = '1TDWB1RAY1FQJT2HVOUZUMHCCYFBJA5EX0Z440OYZIRQTQMP'
consumer_secret = 'XAV035QZG2DTALIHXQZ4CHRPZC4AJZAUTRRSWUEJQKDUTEN3'

# example client using httplib with headers
class SimpleOAuthClient(oauth.OAuthClient):

    def __init__(self, server, port=httplib.HTTP_PORT, request_token_url='', access_token_url='', authorization_url=''):
        self.server = server
        self.port = port
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url
        self.connection = httplib.HTTPConnection("%s:%d" % (self.server, self.port))

    def fetch_request_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method, self.request_token_url, headers=oauth_request.to_header()) 
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def fetch_access_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method, self.access_token_url, headers=oauth_request.to_header()) 
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def authorize_token(self, oauth_request):
        # via url
        # -> typically just some okay response
        self.connection.request(oauth_request.http_method, oauth_request.to_url()) 
        response = self.connection.getresponse()
        return response.read()

    def access_resource(self, oauth_request):
        # via post body
        # -> some protected resources
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        self.connection.request('POST', RESOURCE_URL, body=oauth_request.to_postdata(), headers=headers)
        response = self.connection.getresponse()
        return response.read()


class Registration(webapp.RequestHandler):
    self.requestAuthorization = """
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
        client = SimpleOAuthClient('foursquare.com', 80,
                    Request_Token_URL, Access_Token_URL, Authorize_URL)
        consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        # Did we get here to register, or with a response?
        # TODO: This test won't work if auth fails
        if (request.get("oauth_token") == "":
            # Get the temporary auth token
            oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, 
                    callback=Callback_URL, http_url=client.request_token_url)
            oauth_request.sign_request(signature_method_hmac_sha1, consumer, None)
            print 'REQUEST (via headers)'
            print 'parameters: %s' % str(oauth_request.parameters)
            token = client.fetch_request_token(oauth_request)
            print 'GOT'
            print 'key: %s' % str(token.key)
            print 'secret: %s' % str(token.secret)
            print 'callback confirmed? %s' % str(token.callback_confirmed)

            # Construct the request URL
            oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=client.authorization_url)
            print 'REQUEST (via url query string)'
            print 'parameters: %s' % str(oauth_request.parameters)

            self.response.out.write(
                self.requestAuthorization % { 'url': oauth_request.to_url() }
            )
        else:
            # Check the auth token by converting it into a token + secret
            print '* Obtain an access token ...'
            oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                consumer, token=token, verifier=verifier, 
                http_url=client.access_token_url)
            oauth_request.sign_request(signature_method_plaintext, consumer, token)
            print 'REQUEST (via headers)'
            print 'parameters: %s' % str(oauth_request.parameters)
            token = client.fetch_access_token(oauth_request)
            print 'GOT'
            print 'key: %s' % str(token.key)
            print 'secret: %s' % str(token.secret)

            # Store those in the database and let them know we're good
            self.response.out.write(self.gotAuthorization)
