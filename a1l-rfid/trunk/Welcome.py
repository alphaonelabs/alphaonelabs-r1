import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class Welcome(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 
                'templates','welcome.html')
        self.response.out.write(template.render(path, template_values))
