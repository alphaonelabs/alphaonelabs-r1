from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from datetime import datetime
import logging
import traceback
import sys

DATE_FORMAT="%Y/%m/%d %H:%M:%S"

class RFIDLogger(webapp.RequestHandler):
    def post(self):
        return self.get()

    def get(self):
        logging.getLogger().setLevel(logging.debug)
        logging.debug("starting log")
        startDate = datetime.min
        try:
            startDate = datetime.strptime(self.request.get('start'),DATE_FORMAT)
        except:
            pass

        logging.debug("a")
        print ("a", file=sys.stderr)
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
        print("startDate "+str(startDate)+" endDate "+str(endDate)+" rowcount "+str(rowcount), file=sys.stderr)
        try:
            query = db.GqlQuery("select * from AccessLog where access_time >= :1 and access_time <= :2 order by access_time desc limit :3", \
                startDate, endDate, rowcount)

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
