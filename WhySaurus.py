import fix_path
import cgi
import datetime
import urllib
import wsgiref.handlers
import os
import string
import json
import facebook
import logging

import webapp2 as webapp

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch

from google.appengine.ext.webapp.util import run_wsgi_app

from WhySaurusModels import Point
from WhySaurusModels import PointRoot
from WhySaurusModels import User

DEV = os.environ['SERVER_SOFTWARE'].startswith('Development')

if DEV:
  fbsettings = {
    'FACEBOOK_APP_ID':"460138394028773",
    'FACEBOOK_APP_SECRET' : "ae64953822e937d9fed9daaa959390e9",
    'FACEBOOK_CHANNEL_URL' : "//localhost:8081/channel.html"
  }
else:
  fbsettings = {
    'FACEBOOK_APP_ID' : "437336826315160",
    'FACEBOOK_APP_SECRET' : "d09e82124bccb0336237f2b62a5187c4",
    'FACEBOOK_CHANNEL_URL' : "http://whysaurus-beta.appspot.com/channel.html"
  }


# ***************************************************************************************
#  MAIN PAGE STUFF 
# ***************************************************************************************		
def prepareTemplateValuesForMain(pageHandler):
  pointsQuery = Point.gql("WHERE current = TRUE ORDER BY dateEdited DESC")
  points = pointsQuery.fetch(100)
  user = pageHandler.current_user
  # GET RECENTLY VIEWED
  if user:
    recentlyViewedPoints = user.getRecentlyViewed()
  else:
    recentlyViewedPoints = []

  # GET EDITORS PICKS
  editorsPicksPoints = PointRoot.getEditorsPicks()
  
  template_values = {
  	'points': points,
  	'editorsPicks':editorsPicksPoints,
  	'recentlyViewed':recentlyViewedPoints,
    'dev': DEV,
  	'user':user,
  	'fbsettings':fbsettings
  }
  return template_values
		
class WhysaurusRequestHandler(webapp.RequestHandler):
  """Provides access to the active Facebook user in self.current_user

  The property is lazy-loaded on first access, using the cookie saved
  by the Facebook JavaScript SDK to determine the user ID of the active
  user. See http://developers.facebook.com/docs/authentication/ for
  more information.
  """
  @property
  def current_user(self):
    if not hasattr(self, "_current_user"):
      self._current_user = None   
      logging.info(">>> Cookies received: " + str(self.request.cookies) + " FB APP ID: " + fbsettings['FACEBOOK_APP_ID'])
      cookie = facebook.get_user_from_cookie(
        self.request.cookies, fbsettings['FACEBOOK_APP_ID'], fbsettings['FACEBOOK_APP_SECRET'])
      if cookie:
        logging.info(">>> Trying to get user: " + "fb:"+cookie["uid"])
        # Store a local instance of the user data so we don't need
        # a round-trip to Facebook on every request
        user = User.get_by_key_name("fb:"+cookie["uid"])
        if not user:
          logging.info(">>> Did not get user. Going to facebook.")
          graph = facebook.GraphAPI(cookie["access_token"])
          profile = graph.get_object("me")
          user = User(key_name="fb:"+str(profile["id"]),
                      id=str(profile["id"]),
                      name=profile["name"],
                      profile_url=profile["link"],
                      access_token=cookie["access_token"],
                      admin=False,
                      recentlyViewedRootKeys = [])
          user.put()
        elif user.access_token != cookie["access_token"]:
          user.access_token = cookie["access_token"]
          user.put()
        self._current_user = user
      return self._current_user
      
class MainPage(WhysaurusRequestHandler):
	def get(self):     
		path = os.path.join(os.path.dirname(__file__), 'index.html')
	 	self.response.out.write(template.render(path, prepareTemplateValuesForMain(self)))


# ***************************************************************************************
#  POINT HANDLERS
# ***************************************************************************************

class NewPoint(WhysaurusRequestHandler):
  def post(self):
    user = self.current_user
    if user:
      newPoint = Point.create(self.request.get('title'),self.request.get('content'),user)['point']
      template_values = {
        'point': newPoint,
        'user' : user,
        'fbsettings':fbsettings
      }
      path = os.path.join(os.path.dirname(__file__), 'newpoint.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.out.write('Need to be logged in')


class DeletePoint(WhysaurusRequestHandler):
  def post(self):
    resultJSON = json.dumps({'result':False, 'error':'Point Not Found'})
    user = self.current_user
    if not user:
      resultJSON = json.dumps({'result':False, 'error':'Need to be logged in'})
    elif not user.admin:
      resultJSON = json.dumps({'result':False, 'error':'Must be admin'})
    else:   
      urlToDelete = self.request.get('urlToDelete');
      pointRootQuery = PointRoot.gql("WHERE url= :1", urlToDelete)
      pointRoot = pointRootQuery.get()

      if pointRoot:
        if pointRoot.pointsSupportedByMe:
          resultJSON = json.dumps({'result':False, 'error':'Cannot delete this point as it supports other points'})
        else:
          pointQuery = Point.gql("WHERE ANCESTOR IS :1 ", pointRoot)
          points = pointQuery.fetch(50) # Only 50 for now
          for point in points:
          	point.delete()
          pointRoot.delete()
          resultJSON = json.dumps({'result':True, 'deletedURL':urlToDelete })
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)

class ViewPoint(WhysaurusRequestHandler):
  def get(self, pointURL):
    # check if dev environment for Disqus
    if DEV:
    	devInt = 1
    else:
    	devInt = 0
    pointAndRoot = Point.getCurrentByUrl(pointURL)
    if pointAndRoot:
      point = pointAndRoot['point']
      supportingPoints = point.getSupportingPoints()
      user = self.current_user
      if not user or not user.userVotes or not str(point.parent().key()) in user.userVotes.keys(): 
        voteValue = 0
      else:
        voteValue = user.userVotes[str(point.parent().key())].value

      addedToRecentlyViewed = False      
      if user:
        addedToRecentlyViewed = user.updateRecentlyViewed(str(point.parent().key()))

      # For now add to a point's view count if user is not logged in or if view point is added to the recently viewed list
      if addedToRecentlyViewed or not user:
        pointAndRoot['pointRoot'].addViewCount()

      template_values = {
      	'point': point,
      	'pointRoot': pointAndRoot['pointRoot'],
      	'numPoints': len(point.supportingPoints),
      	'supportingPoints': supportingPoints,
      	'user': user,
      	'devInt': devInt, # For Disqus
      	'voteValue': voteValue,
      	'fbsettings': fbsettings
      }
      path = os.path.join(os.path.dirname(__file__), 'point.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.out.write('Could not find point: ' + pointURL)

# AJAX. CALLED FROM THE POINT VIEW PAGE
class EditPoint(WhysaurusRequestHandler):
  def post(self): 
    resultJSON = json.dumps({'result':False})
    if self.request.get('pointKey'):
      oldPoint = Point.get(db.Key(self.request.get('pointKey')))
    else:
      oldPointAndRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
      oldPoint = oldPointAndRoot['point']

    newVersion = oldPoint.update(
      newTitle=self.request.get('title'), 
      newContent=self.request.get('content'),
      user=self.current_user 
      )
    if newVersion:
      resultJSON = json.dumps({'result':True, 
        'version':newVersion.version,
        'author':newVersion.authorName,
        'dateEdited':str(newVersion.dateEdited),
        'key':str(newVersion.key()),
        })
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)
    
class UnlinkPoint(WhysaurusRequestHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    if self.request.get('mainPointKey'):
      mainPoint = Point.get(db.Key(self.request.get('mainPointKey')))
    if self.request.get('supportingPointKey'):
      newVersion = mainPoint.unlink(self.request.get('supportingPointKey'), self.current_user)
      if newVersion:
        resultJSON = json.dumps({'result':True, 'pointKey':str(newVersion.key())})
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)
    
class LinkPoint(WhysaurusRequestHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    supportingPointAndRoot = Point.getCurrentByUrl(self.request.get('supportingPointURL'))
    oldPointAndRoot = Point.getCurrentByUrl(self.request.get('parentPointURL'))
    oldPoint = oldPointAndRoot['point']
    supportingPoint = supportingPointAndRoot['point']
    supportingPointRoot = supportingPointAndRoot['pointRoot']
    
    user = self.current_user
    if user:      
      newPoint = oldPoint.update(
        newSupportingPoint=str(supportingPointRoot.key()),
        user=user
        )
      supportingPointRoot.addSupportedPoint(oldPoint.parent_key())
      resultJSON = json.dumps({'result':True})
    else:
      resultJSON = json.dumps({'result':'ACCESS DENIED!'})
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)   

class SelectSupportingPoint(WhysaurusRequestHandler):
  def post(self):
    user = self.current_user
    # GET RECENTLY VIEWED
    if user:
      oldPointAndRoot = Point.getCurrentByUrl(self.request.get('parentPointURL'))
      oldPoint = oldPointAndRoot['point']
      recentlyViewedPoints = user.getRecentlyViewed(excludeList = [str(oldPoint.parent_key())])
    else:
      recentlyViewedPoints = []

    templateValues = {
      'points': recentlyViewedPoints,
      'parentPoint': oldPoint,
			'user' : user,
			'fbsettings':fbsettings
    }
    path = os.path.join(os.path.dirname(__file__), 'selectSupportingPoint.html')
    self.response.out.write(template.render(path, templateValues ))
  	
class PointHistory(WhysaurusRequestHandler):
  def get(self):
    points = Point.getAllByUrl(self.request.get('pointUrl'), "ORDER BY version DESC")
    mainAndSupporting = [] # An array of mainPoint - supportingPoints pairs

    if points:
      for mainPoint in points:
        supportingPoints = mainPoint.getSupportingPoints()
        mainAndSupporting.append({"mainPoint":mainPoint, "supportingPoints":supportingPoints})

      template_values = {
        'latestPoint' : points[0],
        'points': points,
        'num_points': len(points),
        'mainAndSupporting': mainAndSupporting,
        'user' : self.current_user
      }

      self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
      self.response.out.write(resultJSON)


class AddSupportingPoint(WhysaurusRequestHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    oldPointAndRoot = Point.getCurrentByUrl(self.request.get('pointUrl'))
    oldPoint = oldPointAndRoot['point']
    
    user = self.current_user
    if user:
      supportingPointAndRoot = Point.create(self.request.get('title'), self.request.get('content'), user, oldPoint.parent_key())      
      newPoint = oldPoint.update(
        newSupportingPoint=str(supportingPointAndRoot["pointRoot"].key()),
        user=user
        )

      resultJSON = json.dumps({
        'result':True,
        'point': newPoint,
        'supportingPoint': supportingPointAndRoot['point'],
        'user' : user,
        'fbsettings':fbsettings
      })
      path = os.path.join(os.path.dirname(__file__), 'newsupportingpoint.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.out.write('Need to be logged in')

class Vote(WhysaurusRequestHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    point = Point.get(self.request.get('pointKey'))
    user = self.current_user
    if point and user:
      if user.addVote(point, int(self.request.get('vote'))):
        resultJSON = json.dumps({'result':True, 'newVote':self.request.get('vote')})
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)
    
class TestPage(WhysaurusRequestHandler):
  def get(self):
    user = self.current_user
    template_values = {
      'user' : user,
      'fbsettings':fbsettings
    }
    path = os.path.join(os.path.dirname(__file__), 'test.html')
    self.response.out.write(template.render(path, template_values))
                   
app = webapp.WSGIApplication([
	(r'/', MainPage),
  ('/newPoint', NewPoint),
  ('/deletePoint', DeletePoint),
	('/editPoint', EditPoint),
	('/unlinkPoint', UnlinkPoint),
	(r'/point/(.*)', ViewPoint),
	('/addSupportingPoint', AddSupportingPoint),
	('/selectSupportingPoint', SelectSupportingPoint),
  ('/linkPoint', LinkPoint),	
	('/vote', Vote),
	('/testPage', TestPage),
	('/pointHistory',PointHistory)
], debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()