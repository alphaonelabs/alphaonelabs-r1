from google.appengine.ext import webapp

class Welcome(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
        <html>
            <head>
                <title>Alpha One Labs RFID System</title>
                <script src='mainpage.js'></script>
            </head>
            <body>
            <h1>Welcome to the Alpha One Labs RFID system</h1>
            <input type='button' onclick='load_users()' value="See who's been here"/>
            <input type='button' onclick='register()' value="Register a new user"/>
            </body>
        </html>
        """)
