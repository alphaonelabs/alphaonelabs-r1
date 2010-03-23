from datetime import datetime
import logging
import os
import sys
import traceback

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

class RFIDLogger(webapp.RequestHandler):
    def post(self):
        return self.get()

    def get(self):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("starting log")
        startDate = datetime(1900, 1, 1)
        nowflag = True
        if self.request.get('now') != None and self.request.get('now') != 'now':
            nowflag = False
        if self.request.get('submit') == None or self.request.get('submit') == "":
            nowflag = True

        try:
            startDate = datetime.strptime(self.request.get('start'), DATE_FORMAT)
        except:
            pass

        endDate = datetime.now()
        try:
            if not nowflag:
                endDate = datetime.strptime(self.request.get('end'), DATE_FORMAT)
        except:
            pass

        rowcount = 20
        try:
            rowcount = int(self.request.get('count'))
        except:
            pass

        logging.info("startDate " + str(startDate) + " endDate " + str(endDate) + " rowcount " + str(rowcount) + " now " + str(nowflag))
        try:
            query = db.GqlQuery("select * from AccessLog where access_time >= :1 and access_time <= :2 order by access_time desc ", \
                                startDate, endDate)

            template_values = {
                'start': datetime.strftime(startDate, DATE_FORMAT),
                'end': datetime.strftime(endDate, DATE_FORMAT),
                'now': nowflag,
                'count': rowcount,
                'data': query.fetch(rowcount)
            }

            path = os.path.join(os.path.dirname(__file__), 
                                'templates', 'log.html')
            self.response.out.write(template.render(path, template_values))
        except Exception, e:
            logging.error("Failed log request: " + str(e))
            traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], 
                                      sys.exc_info()[2], 5, sys.stderr)
