from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from datetime import datetime
import logging

DATE_FORMAT="%Y/%m/%d %H:%M:%S"

class Logger(webapp.RequestHandler):
    def get(self):
        logging.getLogger().setLevel(logging.debug)
        logging.debug("starting log")
        startDate = datetime.min
        try:
            startDate = datetime.strptime(self.request.get('start'),DATE_FORMAT)
        except:
            pass
        logging.debug("a")
        endDate = datetime.now()
        try:
            endDate = datetime.strptime(self.request.get('end'),DATE_FORMAT)
        except:
            pass
        logging.debug("b")
        count = 20
        try:
            count = int(self.request.get('count'))
        except:
            pass

        logging.info("startDate "+str(startDate)+" endDate "+str(endDate)+" count "+str(count))
        query = db.GqlQuery("select * from AccessLog where access_time >= :1 and access_time <= :2 order by access_time desc limit :3",
            startDate, endDate, count)

        template_values = { 
                            'start': datetime.strftime(startDate, DATE_FORMAT),
                            'end': datetime.strftime(endDate, DATE_FORMAT),
                            'count': count,
                            'data': query.fetch(count)
                          }

        path = os.path.join(os.path.dirname(__file__), 
                'templates','log.html')
        self.response.out.write(template.render(path, template_values))
