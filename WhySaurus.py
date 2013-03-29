import os
import json
import constants
import logging
import django

import webapp2
from webapp2 import Route, WSGIApplication
from webapp2_extras import auth, sessions, jinja2
from jinja2 import exceptions

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail

from WhySaurusModels import Point, WhysaurusException
from WhySaurusModels import PointRoot
from WhySaurusModels import WhysaurusUser

from simpleauth import SimpleAuthHandler

class WhysaurusRequestHandler(webapp2.RequestHandler):
  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)

    try:
      # Dispatch the request.
      webapp2.RequestHandler.dispatch(self)      
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)
         
  @webapp2.cached_property
  def session(self):
    """Returns a session using the default cookie key"""
    return self.session_store.get_session()

  @webapp2.cached_property
  def auth(self):
    return auth.get_auth()

  @webapp2.cached_property
  def current_user(self):
    """Returns currently logged in user"""
    user_dict = self.auth.get_user_by_session()
    if user_dict and user_dict['user_id'] is not None:
      return self.auth.store.user_model.get_by_id(user_dict['user_id'])
    else:
      return None

  @webapp2.cached_property
  def logged_in(self):
    """Returns true if a user is currently logged in, false otherwise"""
    return self.auth.get_user_by_session() is not None
    
  def render(self, template_name, template_vars={}):
    # Preset values for the template
    values = {
      'url_for': self.uri_for,
      'logged_in': self.logged_in,
      'flashes': self.session.get_flashes()
    }

    # Add manually supplied template values
    values.update(template_vars)

    # read the template or 404
    try:
      self.response.write(self.jinja2.render_template(template_name, **values))
    except exceptions.TemplateNotFound :
      self.abort(404)

  def head(self, *args):
    """Head is used by Twitter. If not there the tweet button shows 0"""
    pass     


class AuthHandler(WhysaurusRequestHandler, SimpleAuthHandler):
  """Inherits from gae-simpleaiuth (SimpleAuthHandler)
     Authentication handler for OAuth 2.0, 1.0(a) and OpenID."""

  # Enable optional OAuth 2.0 CSRF guard
  OAUTH2_CSRF_STATE = True

  USER_ATTRS = {
    'facebook' : {
      'id'     : lambda id: ('avatar_url', 
        'http://graph.facebook.com/{0}/picture?type=square'.format(id)),
      'name'   : 'name',
      'link'   : 'link',
      'email'  : 'email'
    },
    'google'   : {
      'picture': 'avatar_url',
      'name'   : 'name',
      'link'   : 'link',
      'email'  : 'email'
    },
    'windows_live': {
      'avatar_url': 'avatar_url',
      'name'      : 'name',
      'link'      : 'link'
    },
    'twitter'  : {
      'profile_image_url': 'avatar_url',
      'screen_name'      : 'name',
      'link'             : 'link'
    },
    'linkedin' : { # This is disable for now due to no lxml
      'picture-url'       : 'avatar_url',
      'first-name'        : 'name',
      'public-profile-url': 'link'
    },
    'openid'   : {
      'id'      : lambda id: ('avatar_url', '/img/missing-avatar.png'),
      'nickname': 'name',
      'email'   : 'link'
    }
  }
  
  

  def _on_signin(self, data, auth_info, provider):
    auth_id = '%s:%s' % (provider, data['id'])
    logging.info('Looking for a user with id %s', auth_id)
    
    user = self.auth.store.user_model.get_by_auth_id(auth_id)
    _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])
    if user:
      logging.info('Found existing user to log in')
      # Existing users might've changed their profile data so we update our
      # local model anyway. This might result in quite inefficient usage
      # of the Datastore, but we do this anyway for demo purposes.
      #
      # In a real app you could compare _attrs with user's properties fetched
      # from the datastore and update local user in case something's changed.
      user.populate(**_attrs)
      user.put()
      self.auth.set_session( self.auth.store.user_to_dict(user))
      
    else:
      # check whether there's a user currently logged in
      # then, create a new user if nobody's signed in, 
      # otherwise add this auth_id to currently logged in user.

      if self.logged_in and self.current_user:
        logging.info('Updating currently logged in user')
        
        u = self.current_user
        u.populate(**_attrs)
        # The following will also do u.put(). Though, in a real app
        # you might want to check the result, which is
        # (boolean, info) tuple where boolean == True indicates success
        # See webapp2_extras.appengine.auth.models.User for details.
        u.add_auth_id(auth_id)
        
      else:
        logging.info('Creating a brand new user. Auth_id: %s ', str(auth_id))
        ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
        if ok:
          self.auth.set_session(self.auth.store.user_to_dict(user))
        else:
          logging.info('Creation failed: ' + str(ok))
    # Remember auth data during redirect, just for this demo. You wouldn't
    # normally do this.
    # self.session.add_flash(data, 'data - from _on_signin(...)')
    # self.session.add_flash(auth_info, 'auth_info - from _on_signin(...)')

    # Go to the profile page
    target = str(self.session['original_url'])
    self.redirect(target)
    
  def logout(self):
    self.auth.unset_session()
    self.redirect('/')

  def _callback_uri_for(self, provider):
    return self.uri_for('auth_callback', provider=provider, _full=True)

  def _get_consumer_info_for(self, provider):
    """Should return a tuple (key, secret) for auth init requests.
    For OAuth 2.0 you should also return a scope, e.g.
    ('my app id', 'my app secret', 'email,user_about_me')
    
    The scope depends solely on the provider.
    """
    return constants.AUTH_CONFIG[provider]
    
  def _to_user_model_attrs(self, data, attrs_map):
    """Get the needed information from the provider dataset."""
    user_attrs = {}
    for k, v in attrs_map.iteritems():
      attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
      user_attrs.setdefault(*attr)    
    return user_attrs
            
class MainPage(AuthHandler):
  def get(self): 
        
    newPoints = PointRoot.getRecentCurrentPoints()
    user = None
    
    if self.logged_in:
      user = self.current_user
  
    # GET RECENTLY VIEWED
    if user:
      recentlyViewedPoints = user.getRecentlyViewed()
    else:
      recentlyViewedPoints = []
  
    editorsPicksPoints = PointRoot.getEditorsPicks()
    topPoints = PointRoot.getTopRatedPoints()
    template_values = {
      'newPoints': newPoints,
      'topPoints': topPoints,
      'editorsPicks':editorsPicksPoints,
      'recentlyViewed':recentlyViewedPoints,
      'user':user,
      'thresholds' : constants.SCORETHRESHOLDS
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))


class NewPoint(AuthHandler):
  def post(self):
    user = self.current_user
    resultJSON = json.dumps({'result':False, 'error':'Not authorized'})
    if user:
      newPoint, newPointRoot = Point.create(
        title=self.request.get('title'),
        content=self.request.get('content'), 
        summaryText=self.request.get('plainText'),
        user=user,
        imageURL=self.request.get('imageURL'),
        imageAuthor=self.request.get('imageAuthor'),
        imageDescription=self.request.get('imageDescription'))
      if newPoint:
        resultJSON = json.dumps({'result':True, 'pointURL':newPoint.url })
      else:
        resultJSON = json.dumps({'result':False, 'error':'Failed to create point.' })
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)


class DeletePoint(AuthHandler):
  def post(self):
    resultJSON = json.dumps({'result':False, 'error':'Point Not Found'})
    user = self.current_user
    if not user:
      resultJSON = json.dumps({'result':False, 'error':'Need to be logged in'})
    elif not user.admin:
      resultJSON = json.dumps({'result':False, 'error':'Must be admin'})
    else:   
      urlToDelete = self.request.get('urlToDelete');
      point, pointRoot = Point.getCurrentByUrl(urlToDelete)

      if pointRoot:
        result, error = pointRoot.delete(user)
        if result:
          resultJSON = json.dumps({'result':True, 'deletedURL':urlToDelete })
        else:
          resultJSON = json.dumps({'result':False, 'error':error})
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)

class ViewPoint(AuthHandler):
  def get(self, pointURL):
    # check if dev environment for Disqus
    devInt = 1 if constants.DEV else 0

    point, pointRoot = Point.getCurrentByUrl(pointURL)
    if point:
      supportingPoints = point.getSupportingPoints()
      user = self.current_user
      if not user or not user.userVotes or not point.key.parent() in user.userVotes: 
        voteValue = 0
      else:
        voteValue = user.userVotes[point.key.parent()].value

      addedToRecentlyViewed = False      
      if user:
        addedToRecentlyViewed = user.updateRecentlyViewed(point.key.parent())

      # For now add to a point's view count if user is not logged in or if view point is added to the recently viewed list
      if addedToRecentlyViewed or not user:
        pointRoot.addViewCount()
        
      template_values = {
      	'point': point,
      	'pointRoot': pointRoot,
      	'numPoints': len(point.supportingPoints),
      	'supportingPoints': supportingPoints,
      	'user': user,
      	'devInt': devInt, # For Disqus
      	'voteValue': voteValue,
        'thresholds' : constants.SCORETHRESHOLDS
      }
      path = os.path.join(os.path.dirname(__file__), 'templates/point.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.response.out.write('Could not find point: ' + pointURL)

# AJAX. CALLED FROM THE POINT VIEW PAGE
class EditPoint(AuthHandler):
  def post(self): 
    resultJSON = json.dumps({'result':False})
    oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('urlToEdit'))
    newVersion = oldPoint.update(
      newTitle=self.request.get('title'), 
      newContent=self.request.get('content'),
      newSummaryText=self.request.get('plainText'),
      user=self.current_user,
      imageURL=self.request.get('imageURL'),
      imageAuthor=self.request.get('imageAuthor'),
      imageDescription=self.request.get('imageDescription') 
      )
    if newVersion:
      resultJSON = json.dumps({'result':True, 
        'version':newVersion.version,
        'author':newVersion.authorName,
        'dateEdited': str(newVersion.dateEdited),
        'imageURL': newVersion.imageURL,
        'imageAuthor': newVersion.imageAuthor,
        'imageDescription': newVersion.imageDescription 
        })
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)
    
class UnlinkPoint(AuthHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    if self.request.get('mainPointURL'):
      mainPoint, pointRoot = Point.getCurrentByUrl(self.request.get('mainPointURL'))
      if self.request.get('supportingPointURL'):
        supportingPointURL = self.request.get('supportingPointURL')
        newVersion = mainPoint.unlink(self.request.get('supportingPointURL'), self.current_user)
        if newVersion:
          resultJSON = json.dumps({'result':True, 'pointURL':supportingPointURL})
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)
    
class LinkPoint(AuthHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    supportingPoint, supportingPointRoot = Point.getCurrentByUrl(self.request.get('supportingPointURL'))
    oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('parentPointURL'))   
    user = self.current_user
    
    if user:      
      try:
        newPoint = oldPoint.update(
          newSupportingPoint=supportingPointRoot,
          user=user
          )
      except WhysaurusException as e:
        resultJSON = json.dumps({'result':False, 'error': str(e)})
      else:   
        resultJSON = json.dumps({'result':True})
    else:
      resultJSON = json.dumps({'result':'ACCESS DENIED!'})
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)   

class SelectSupportingPoint(AuthHandler):
  def post(self):
    user = self.current_user
    # GET RECENTLY VIEWED
    if user:
      oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('parentPointURL'))
      recentlyViewedPoints = user.getRecentlyViewed(
                                                    excludeList = 
                                                    [oldPoint.key.parent()] + oldPoint.supportingPoints 
                                                     )
    else:
      recentlyViewedPoints = []

    templateValues = {
      'points': recentlyViewedPoints,
      'parentPoint': oldPoint,
			'user' : user,
      'thresholds' : constants.SCORETHRESHOLDS
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/selectSupportingPoint.html')
    self.response.out.write(template.render(path, templateValues ))

class PointHistory(AuthHandler):
  def get(self):
    pointData = Point.getFullHistory(self.request.get('pointUrl'))
    
    template_values = {
      'latestPoint' : pointData[0]["point"] if pointData else None,
      'numPoints': len(pointData) if pointData else 0,
      'pointData': pointData,
      'user' : self.current_user
    }

    path = os.path.join(os.path.dirname(__file__), 'templates/pointHistory.html')
    self.response.out.write(template.render(path, template_values ))


class AddSupportingPoint(AuthHandler):
  def post(self):
    jsonOutput = {'result':False}
    oldPoint, oldPointRoot = Point.getCurrentByUrl(self.request.get('pointUrl'))
    user = self.current_user
    
    if user:
      supportingPoint, supportingPointRoot = Point.create(
        title=self.request.get('title'), 
        content=self.request.get('content'),
        summaryText=self.request.get('plainText'),
        user=user,        
        pointSupported=oldPoint.key.parent(),
        imageURL=self.request.get('imageURL'),
        imageAuthor=self.request.get('imageAuthor'),
        imageDescription=self.request.get('imageDescription'))     
      try: 
        newPoint = oldPoint.update(
          newSupportingPoint=supportingPointRoot,
          user=user
          )
      except WhysaurusException as e:
        jsonOutput = {
          'result':False,
          'err':str(e)
        }
      else: 
        jsonOutput = {
          'result':True,
          'version':newPoint.version,
          'author':newPoint.authorName,
          'dateEdited':newPoint.dateEdited.strftime("%Y-%m-%d %H:%M:%S %p"),
        }
      resultJSON = json.dumps(jsonOutput)
      self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
      self.response.out.write(resultJSON)  
    else:
      self.response.out.write('Need to be logged in')

class Vote(AuthHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    point, pointRoot = Point.getCurrentByUrl(self.request.get('pointURL'))
    user = self.current_user
    if point and user:
      logging.info('ADDING VOTE')
      if user.addVote(point, int(self.request.get('vote'))):
        resultJSON = json.dumps({'result':True, 'newVote':self.request.get('vote')})
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)
 
class Search(AuthHandler):
  def get(self):
    searchResults = Point.search(self.request.get('searchTerms'))
    template_values = {
      'user': self.current_user,
      'searchResults' : searchResults,
      'searchString': self.request.get('searchTerms'),
      'thresholds' : constants.SCORETHRESHOLDS
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/searchResults.html')
    self.response.out.write(template.render(path, template_values))

class AjaxSearch(AuthHandler):
  def post(self):
    resultJSON = json.dumps({'result':False})
    searchResults = Point.search(self.request.get('searchTerms'), self.request.get('exclude'))
    if searchResults:
      resultJSON = json.dumps( {
        'result': True,
        'searchResults' : searchResults,
        'searchString': self.request.get('searchTerms')
      })
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    self.response.out.write(resultJSON)   
    
class TestPage(AuthHandler):
  def get(self):
    user = self.current_user
    template_values = {
      'user' : user,
      'dv': django.VERSION
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/test.html')
    self.response.out.write(template.render(path, template_values))

    
class About(AuthHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
    self.response.out.write(template.render(path, {'user' : self.current_user}))   
        
class Help(AuthHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/help.html')
    self.response.out.write(template.render(path, {'user' : self.current_user}))     
        
class Contact(AuthHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/contact.html')
    self.response.out.write(template.render(path, {'user' : self.current_user}))   

class ContactSend(AuthHandler):
  def post(self):
    mail.send_mail(sender='aaron@whysaurus.com',
       to= 'aaronlifshin@gmail.com',
       subject= 'WHYSAURUS CONTACT RE:' + self.request.get('subject'), 
       body= 'From: ' + self.request.get('name') + '\n' + self.request.get('message'),
       reply_to=self.request.get('email')
    )
    
    template_values = {
      'message' : "Thank you for your message.",
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/message.html')
    self.response.out.write(template.render(path, template_values))
    
    
# Map URLs to handlers
routes = [
	Route('/', MainPage),
  Route('/about', About),
  Route('/help', Help),
  Route('/contact', Contact),
  Route('/contactSend', ContactSend),
  Route('/newPoint', NewPoint),
  Route('/deletePoint', DeletePoint),
	Route('/editPoint', EditPoint),
	Route('/unlinkPoint', UnlinkPoint),
	Route('/point/<pointURL>', ViewPoint),
	Route('/addSupportingPoint', AddSupportingPoint),
	Route('/selectSupportingPoint', SelectSupportingPoint),
  Route('/linkPoint', LinkPoint),	
	Route('/vote', Vote),
	Route('/testPage', TestPage),
  Route('/search', Search),
  Route('/ajaxSearch', AjaxSearch),
	Route('/pointHistory',PointHistory), 
  # Route('/profile', handler='handlers.ProfileHandler', name='profile'),
  Route('/logout', handler='WhySaurus.AuthHandler:logout', name='logout'), # , handler_method='logout', name='logout'),
  Route('/auth/<provider>', handler='WhySaurus.AuthHandler:_simple_auth', name='auth_login') , 
  Route('/auth/<provider>/callback', handler='WhySaurus.AuthHandler:_auth_callback', name='auth_callback')
]
  
# webapp2 config
app_config = {
  'webapp2_extras.sessions': {
    'cookie_name': '_simpleauth_sess',
    'secret_key': constants.SESSION_KEY
  },
  'webapp2_extras.auth': {
    'user_attributes': [],
    'user_model': WhysaurusUser
  }
}

app = WSGIApplication(routes=routes, config=app_config, debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()