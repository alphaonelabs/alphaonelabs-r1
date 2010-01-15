import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class Welcome(webapp.RequestHandler):
    def get(self):
        logging.getLogger().setLevel(logging.debug)
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 
                'templates','welcome.html')
        logging.debug("this is a debug message")
        self.response.out.write(template.render(path, template_values))
