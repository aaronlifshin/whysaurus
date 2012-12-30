import fix_path
import cgi
import datetime
import urllib
import wsgiref.handlers
import os
import WhySaurusModels

import webapp2 as webapp

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users

from google.appengine.ext.webapp.util import run_wsgi_app

class admin(webapp.RequestHandler):
	def get(self):
		
		pointsCount = WhySaurusModels.Point.all().count()
		rootsCount = WhySaurusModels.PointRoot.all().count()

		templateArgs = {
			'pointsCount': pointsCount,
			'rootsCount': rootsCount
		}
		path = os.path.join(os.path.dirname(__file__), 'admin.html')
	 	self.response.out.write(template.render(path, templateArgs))
		


app = webapp.WSGIApplication([
	('/admin', admin)
], debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()