import webapp2
import logging
from webapp2_extras import auth, sessions
from jinja2 import exceptions
from google.appengine.api import namespace_manager

class WhysaurusRequestHandler(webapp2.RequestHandler):
       
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            user = self.current_user
            if user:
                sessionArea = self.session.get('currentArea')
                if sessionArea is None: # Sometimes the session seems to expire
                    if user.privateArea and user.privateArea is not None:
                        sessionArea = self.setUserArea(usePrivate=True)
                if sessionArea != '' and sessionArea == user.privateArea:
                    logging.info('SETTING REQUEST NAMESPACE: |%s| ' % self.session.get('currentArea'))
                    namespace_manager.set_namespace(self.session.get('currentArea')) 
                user.getActiveNotifications()
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def setUserArea(self, usePrivate=True):
        theU = self.current_user        
        newArea = ''

        if theU:
            if usePrivate: 
                self.session['currentArea'] = theU.privateArea
                namespace_manager.set_namespace(theU.privateArea) 
                newArea = theU.privateArea         
            else:
                self.session['currentArea'] = ''
                namespace_manager.set_namespace('')     
            return newArea
        else:
            return None
        
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
            previousNamespace = namespace_manager.get_namespace()
            namespace_manager.set_namespace('') # DEFAULT NAMESPACE
            user = self.auth.store.user_model.get_by_id(user_dict['user_id'])        
            namespace_manager.set_namespace(previousNamespace)
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
