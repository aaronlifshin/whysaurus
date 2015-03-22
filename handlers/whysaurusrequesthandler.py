import webapp2
import logging
from webapp2_extras import auth, sessions
from google.appengine.ext import ndb

from jinja2 import exceptions
from google.appengine.api import namespace_manager
from models.privateArea import PrivateArea
from models.document import Document

class WhysaurusRequestHandler(webapp2.RequestHandler):
    _user = None
        
    def dispatch(self):        
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            user = self.current_user
            if user:
                sessionArea = self.session.get('currentArea')
                currentAreaDisplayName = self.session.get('currentAreaDisplayName')
                
                if sessionArea is None: # Sometimes the session seems to expire
                    if len(user.privateAreas) == 1:
                        sessionArea = self.setUserArea(user.privateAreas[0])
                if sessionArea != '' and sessionArea in user.privateAreas:
                    namespace_manager.set_namespace(sessionArea)
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def getCurrentAssignmentKey(self):
        sessionAssignmentKey = None       
        currentArea = self.session.get('currentArea')
        
        if currentArea and currentArea != '':
            sessionAssignmentUrlSafeKey = self.session.get('currentAssignment')
            sessionAssignmentKey = ndb.Key(urlsafe=sessionAssignmentUrlSafeKey)
        return sessionAssignmentKey
    
    def getCurrentAssignment(self):
        currentAssignment = None
        documents = None
        
        sessionAssignmentKey = self.getCurrentAssignmentKey()
        if sessionAssignmentKey:            
            currentAssignment = sessionAssignmentKey.get()
            documents = Document.getAllForAssignment(currentAssignment)
        return currentAssignment, documents
        
    # This has no checks on whether the user is a part of the area
    # in some cases we want to switch the current area
    # even if they're not logged in
    # e.g. to create a user in that area
    def setUserArea(self, area_name):
        u = self.current_user
        if u is None:
            return None

        # Handler doesn't like being called with a blank url var
        # so "public" is our special string to denote... that
        if area_name == 'public':
            area_name = ''

        # Force public if they're trying something uncouth
        if area_name != '' and not area_name in u.privateAreas:
            area_name = ''

        self.session['currentArea'] = area_name
        self.session['currentAreaDisplayName'] = PrivateArea.getDisplayName(area_name)
        namespace_manager.set_namespace(area_name)

        return area_name

    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key"""
        return self.session_store.get_session()

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    # returns the currently logged in user
    @webapp2.cached_property
    def current_user(self):
        if self._user:
            return self._user
        else:    
            """Returns currently logged in user"""
            user_dict = self.auth.get_user_by_session(True)
            if user_dict and user_dict['user_id'] is not None:
                previousNamespace = namespace_manager.get_namespace()
                # USER MODEL IS ALWAYS STORED IN DEFAULT NAMESPACE
                namespace_manager.set_namespace('') 
                user = self.auth.store.user_model.get_by_id(user_dict['user_id']) 
                self._user = user       
                namespace_manager.set_namespace(previousNamespace)
                # self.session['user'] = user
                return user
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
        except exceptions.TemplateNotFound:
            self.abort(404)

    def head(self, *args):
        """Head is used by Twitter. If not there the tweet button shows 0"""
        pass
