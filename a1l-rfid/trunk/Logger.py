from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from datetime import datetime
import logging
import traceback
import sys
import os

DATE_FORMAT="%Y/%m/%d %H:%M:%S"

class RFIDLogger(webapp.RequestHandler):
    def post(self):
        return self.get()

    def get(self):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("starting log")
        startDate = datetime(1900,1,1)
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
        rowcount = 20
        try:
            rowcount = int(self.request.get('count'))
        except:
            pass

        logging.info("startDate "+str(startDate)+" endDate "+str(endDate)+" rowcount "+str(rowcount))
        sys.stderr.write("startDate "+str(startDate)+" endDate "+str(endDate)+" rowcount "+str(rowcount)+"\n")
        try:
            query = db.GqlQuery("select * from AccessLog where access_time >= :1 and access_time <= :2 order by access_time desc ", \
                startDate, endDate)

            template_values = { 
                            'start': datetime.strftime(startDate, DATE_FORMAT),
                            'end': datetime.strftime(endDate, DATE_FORMAT),
                            'count': rowcount,
                            'data': query.fetch(rowcount)
                          }

            path = os.path.join(os.path.dirname(__file__), 
                'templates','log.html')
            self.response.out.write(template.render(path, template_values))
        except Exception, e:
            logging.error("Failed log request: "+str(e))
            traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], 
                                      sys.exc_info()[2], 5, sys.stderr)
