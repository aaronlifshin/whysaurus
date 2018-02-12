import logging
import constants
import json
import os
import webapp2
import jinja2
import time
import gae_mini_profiler.profiler

from simpleauth import SimpleAuthHandler
from whysaurusrequesthandler import WhysaurusRequestHandler
from models.whysaurususer import WhysaurusUser
from models.whysaurusexception import WhysaurusException
from google.appengine.api import namespace_manager


from google.appengine.api import mail
from google.appengine.ext.webapp import template
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from models.reportEvent import ReportEvent
from models.point import Point
from models.reportEvent import ReportEvent
from models.privateArea import PrivateArea
from models.areauser import AreaUser
    
class AuthHandler(WhysaurusRequestHandler, SimpleAuthHandler):
    """Inherits from gae-simpleauth (SimpleAuthHandler)
       Authentication handler for OAuth 2.0, 1.0(a) and OpenID."""

    # Enable optional OAuth 2.0 CSRF guard
    OAUTH2_CSRF_STATE = True

    
    # HOW USER_ATTRS works - a discourse 
    # If str: str - the first argument is used to key into the OAuth Provider data
    # The second argument ends up in the DB model
    # If str: lambda - the first argument keys into the provider data and is passed to the lambda function
    # The lambda function returns, in order, model property name and value
    USER_ATTRS = {
        'facebook': {
            'id': lambda id: ('avatar_url',
                              'https://graph.facebook.com/{0}/picture?type=square'.format(id)),
            'name': 'name',
            'link': 'facebookProfileURL',
            'email': 'email',
        },
        'google': {
            'picture': 'avatar_url',
            'name': 'name',
            'link': 'googleProfileURL',
            'email': 'email',
        },
        'windows_live': {
            'avatar_url': 'avatar_url',
            'name': 'name',
            'link': 'link'
        },
        'twitter': {
            'profile_image_url': 'avatar_url',
            'screen_name': 'name',
            'link': 'twitterProfileURL',
        },
        'linkedin': {  # This is disable for now due to no lxml
            'picture-url': 'avatar_url',
            'first-name': 'name',
            'public-profile-url': 'link'
        },
        'openid': {
            'id': lambda id: ('avatar_url', '/img/missing-avatar.png'),
            'nickname': 'name',
            'email': 'link'
        }
    }        
        
    @webapp2.cached_property
    def jinja2_env(self):        
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates/jinja'),
            extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_'],
            autoescape=True)    
            
    def template_render(self, templateName, templateVals):
        startTime = int(time.time() * 1000)
        html = ''
        engine = constants.TEMPLATE_RENDERING_ENGINE
        if engine == 'jinja':
            t = self.jinja2_env.get_template(templateName)
            html = t.render(templateVals)
        elif engine == 'django':
            path = os.path.join(constants.ROOT, "templates/django/" + templateName)
            html = template.render(path, templateVals)
        else:
            raise WhysaurusException("Unknown template engine specified" )
        endTime = int(time.time() * 1000)
        logging.info("*^*^*^* Rendering %s took %d msec " % (templateName, endTime - startTime))
        return html
        
    def signup(self):
        email = self.request.get('email')
        name = self.request.get('userName')
        password = self.request.get('password')
        website =self.request.get('website')
        areas=self.request.get('areas')
        profession =self.request.get('profession')
        bio=self.request.get('bio')
        try:
            user = WhysaurusUser.signup(self, email, name, password, website, areas, profession, bio)
            results = {'result': True}

            # See if we can log them into a private area
            if 'postloginaction' in self.session:
                # need to figure out how to pass this over to AJAX
                # and what the point creation will look like
                logging.info("Have post login action when signing up as an email user")
            elif len(user.privateAreas) == 1 and not user.admin:
                self.setUserArea(user.privateAreas[0])
                results['redirect'] = "/"
            
            # login newly created user
            auth_id = 'email: %s' %  email
            u = self.auth.get_user_by_password(auth_id, password, remember=True,
              save_session=True)
            user = self.auth.store.user_model.get_by_id(u['user_id'])
            self.current_user = user
            user.login()
            

        except WhysaurusException as e:
            results = {'result': False, 'error': str(e)}

        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        
    def loginBySecretKey(self, secretKey):        
        if (secretKey == 'myballotsecret'):
            auth_id = 'email:fjmartinez3@gmail.com'
            password = 'myballot123'
            u = self.auth.get_user_by_password(auth_id, password, remember=True,
              save_session=True)
            user = self.auth.store.user_model.get_by_id(u['user_id'])
            self.current_user = user
            user.login()
            return
        
    def setPrivateAreaUser(self, areaName):
        if PrivateArea.exists(areaName):
            self.session['currentArea'] = areaName
            self.session['currentAreaDisplayName'] = PrivateArea.getDisplayName(areaName)
            user = self.current_user    
            self.response.out.write(
                self.template_render(
                    'areaCreateUser.html', 
                    {
                        'privateAreaName':areaName,
                        'user':user,
                        'headerHideActions':1
                    }))
        else:
            self.response.out.write('Sorry, that classroom %s does not appear \
                to exist. Click <a href="/">here</a> to go home' % areaName)
            
    def login(self):
        email = self.request.get('login_userEmail')
        password = self.request.get('login_userPassword')
        postLoginAction = self.request.get('login_userAction')
        logging.info("PLA " + postLoginAction)

        if not email:
            self.redirect("/")

        if email.find('@')!=-1:
            auth_id = 'email: %s' %  email
        else:
            auth_id = 'name: %s' % email
        try:
            namespace_manager.set_namespace('')
            u = self.auth.get_user_by_password(auth_id, password, remember=True,
              save_session=True)
            user = self.auth.store.user_model.get_by_id(u['user_id'])
            self.current_user = user

            # See if we can log them into a private area
            if 'postloginaction' in self.session:
                # Public area, no op
                logging.info('There was a post login action, \
                        so the user is not logged into the private area.')
            elif len(user.privateAreas) == 1 and not user.admin:
                # One private area, put 'em in
                self.setUserArea(user.privateAreas[0])
            # Otherwise, public
            # TODO: Maybe log them into their last recently used area

            # record login informaton
            user.login()
            logging.info("PLA 2 " + postLoginAction)
            
            if (postLoginAction == "createFromMain"):
                logging.info("PLA 3" + postLoginAction)
                
                self.session['pointtext'] = self.request.get('login_userPointText')
                self.doPostLoginAction(postLoginAction, self.session)
                return
            else:
                self.redirect("/")
                return
        except InvalidAuthIdError as e:
            message = 'Could not log in user %s because the email or username was not recognized ' % email
        except InvalidPasswordError as e:
            message = 'Could not log in user %s because the password did not match' % email
        except Exception as e:
            message = "Got unknown exception " + str(e)

        self.response.out.write(
            self.template_render('message.html', {'message': message } ))
                  
    def verify(self, *args, **kwargs):
        user_id = kwargs['user_id']
        signup_token = kwargs['signup_token']
        verification_type = kwargs['type']
    
        # it should be something more concise like
        # self.auth.get_user_by_token(user_id, signup_token
        # unfortunately the auth interface does not (yet) allow to manipulate
        # signup tokens concisely
        user, ts = self.auth.store.user_model.get_by_auth_token(int(user_id), 
                                                     signup_token,
                                                     'signup')
        logging.info('Got user: %s' % str(user))
        if not user:
            tokenType = 'Verification' if verification_type == 'v' else 'Password reset'
            message = '%s URL not valid.  %s URLs can only be used once.' % (tokenType, tokenType)           
            logging.info('Could not find any user with id "%s" signup token "%s"',
              user_id, signup_token)
            self.response.out.write(
                self.template_render('message.html', {'message': message} ))                  
        elif verification_type == 'v':
            # store user data in the session
            self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)
            
            # remove signup token, we don't want users to come back with an old link
            self.auth.store.user_model.delete_signup_token(user.get_id(), signup_token)    
            if not user.verified:
                user.verified = True
                user.put()
    
            message = 'User email address has been verified.'
            self.response.out.write(
                self.template_render('message.html', {
                    'message': message, 'user': user } ))
        elif verification_type == 'p':
            # self.auth.unset_session() # The user is not logged in. They can only to reset the password
            # Log in the user, just this once
            self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)
            
            # remove signup token, we don't want users to come back with an old link
            self.auth.store.user_model.delete_signup_token(user.get_id(), signup_token)
            
            logging.info('Got user2: %s' % str(user))
            template_values = {
                      'user': user,
                      'user_id': user_id,
                      'message': 'You have been logged in. Please change the password from the user menu in the upper right.'
                      }
            self.redirect('/changePassword')
        else:
            logging.info('Verification type not supported')
            self.abort(404)
            
    def forgotPassword(self):
        results = {'result': False}
        email = self.request.get('email')
        user = None
        if email.find('@')!=-1:
            user = WhysaurusUser.get_by_email(email)
            if not user:
                logging.info('Could not find any user entry for email %s' % email)
                results['error'] = 'Could not find user entry with email %s' % email
        else:
            user = WhysaurusUser.get_by_name(email)
            if not user:
                logging.info('Could not find any user entry for username %s' % email)
                results['error'] = 'Could not find user entry with username %s' % email
        if user:
            if hasattr(user, 'email') and user.email is not None and user.email != '':
                user_id = user.get_id()
                token = self.auth.store.user_model.create_signup_token(user_id)    
                verification_url = self.uri_for('verification', type='p', user_id=user_id,
                                                signup_token=token, _full=True)                        
                mail.send_mail(sender='Whysaurus <community@whysaurus.com>',
                    to=user.email,
                    subject='Whysaurus password reset',
                    html="A password reset request has been received for your account. <br> \
                        Please reset your password  \
                        <a href=\"%s\">here</a>.<br><br>Thanks,<br>Whysaurus<br> \
                        " % verification_url,
                    body="A password reset request has been received for your account. \n \
                        Please reset your password by visiting this URL:  \
                        %s. \n\n Thanks,\n Whysaurus\n" % verification_url,
                    reply_to="community@whysaurus.com"
                )
                results = {'result': True}
            else:
                results = {'result': True, 
                           'message': 'There is no email on file for this \
                               username. Please email admin@whysaurus.com \
                               and request a password reset.'}

        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
     
    def passwordChangePage(self):    
        self.response.out.write(self.template_render('resetpassword.html', {
            'user': self.current_user, 
            'currentArea':self.session.get('currentArea'),
            'currentAreaDisplayName':self.session.get('currentAreaDisplayName')
        }))
        
    def changePassword(self): 
        password = self.request.get('password1')
        old_token = self.request.get('t')
        user_id = self.request.get('user_id')
        template_values = {}
        template_values['message'] = ""
        template_values['currentArea'] = self.session.get('currentArea')
        template_values['currentAreaDisplayName'] = self.session.get('currentAreaDisplayName')
        user = self.current_user 
        if not password or password != self.request.get('password2'):
            template_values['message']  = "Passwords do not match"
        else:
            # user could be logged in and changing password, or changing it from token
            if not user:
                user, ts = self.auth.store.user_model.get_by_auth_token(
                                            int(user_id), 
                                            old_token,'signup')
            else: # Pass logged in user to the page
                template_values['user'] = user
            if user:
                user.set_password(password)
                user.put()
                if old_token:
                    # remove signup token, we don't want users to come back with an old link
                    self.auth.store.user_model.delete_signup_token(user.get_id(), old_token)
                template_values['message']  = "Password changed successfully. You may now login with the new password."
            else:
                template_values['message']  = "There was an error. Could not change the password."
        self.response.out.write(
            self.template_render('message.html', template_values ))                       
    
    def emailNewPassword(self): 
        pass
    
    def resetPassword(self): 
        results = {'result': False}
        loggedInUser = self.current_user 
        if loggedInUser and loggedInUser.isAdmin:                             
            targetUserUrl = self.request.get('userurl')
            if targetUserUrl:
                u = WhysaurusUser.getByUrl(targetUserUrl)
                if u:
                    newPassword = u.resetPassword()
                    results = {'result': True, 'username': u.name, 'password': newPassword}
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)

    def setUserGaid(self):
        results = {'result': False}
        loggedInUser = self.current_user
        if loggedInUser and loggedInUser.isAdmin:
            targetUserUrl = self.request.get('userurl')
            newGaid = self.request.get('newGaid')
            if targetUserUrl and newGaid:
                u = WhysaurusUser.getByUrl(targetUserUrl)
                if u:
                    u.setUserGaid(newGaid)
                    results = {'result': True, 'username': u.name, 'newGaid': newGaid}
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        
    def setInternalUser(self):
        results = {'result': False}
        loggedInUser = self.current_user
        if loggedInUser and loggedInUser.isAdmin:
            targetUserUrl = self.request.get('userurl')
            if targetUserUrl:
                u = WhysaurusUser.getByUrl(targetUserUrl)
                if u:
                    u.setInternalUser()
                    results = {'result': True, 'username': u.name}
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        

    def _on_signin(self, data, auth_info, provider):
        auth_id = '%s: %s' % (provider, data['id'])
        logging.info('Looking for a user with id %s', auth_id)

        user = self.auth.store.user_model.get_by_auth_id(auth_id)
        _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])
        if user:
            logging.info('Found existing user to log in: ' + str(_attrs))
            # Existing users might've changed their profile data so we update our
            # local model anyway. This might result in quite inefficient usage
            # of the Datastore, but we do this anyway for demo purposes.
            #
            # In a real app you could compare _attrs with user's properties fetched
            # from the datastore and update local user in case something's changed.  

            self.auth.set_session(self.auth.store.user_to_dict(user))
            self.current_user = user
            user.login()
            if 'postloginaction' in self.session:
                logging.info('There was a post login action, so the user is not logged into the private area.')
            elif len(user.privateAreas) > 0 and not user.admin:
                self.setUserArea(user.privateAreas[0])
        else:
            # check whether there's a user currently logged in
            # then, create a new user if nobody's signed in,
            # otherwise add this auth_id to currently logged in user.

            if self.logged_in and self.current_user:
                # This code is currently not triggered, 
                # there is no way to log in again once logged in
                logging.info('Updating currently logged in user')

                u = self.current_user
                u.populate(**_attrs)
                # The following will also do u.put(). Though, in a real app
                # you might want to check the result, which is
                # (boolean, info) tuple where boolean == True indicates success
                # See webapp2_extras.appengine.auth.models.User for details.
                u.add_auth_id(auth_id)
                u.login()

            else:
                logging.info('Creating a brand new user. Auth_id: %s ', str(auth_id))  
                _attrs['url'] = WhysaurusUser.constructURL(_attrs['name'])
                currentArea = self.session.get('currentArea')
                currentAreaDisplayName = self.session.get('currentAreaDisplayName')
                if currentArea:                    
                    _attrs['privateAreas'] = [currentArea]
                
                ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
                if ok:
                    if currentArea:
                        areaUser = AreaUser(userKey=user.key.urlsafe(), privateArea=currentArea)
                        areaUser.putUnique()
                    user.login()
                    self.current_user = user
                    self.auth.set_session(self.auth.store.user_to_dict(user))
                    ReportEvent.queueEventRecord(user.key.urlsafe(), None, None, "New User")
                    user.addToSearchIndex()                                                               
                else:
                    logging.info('Creation failed: ' + str(ok))
        # Remember auth data during redirect, just for this demo. You wouldn't
        # normally do this.
        # self.session.add_flash(data, 'data - from _on_signin(...)')
        # self.session.add_flash(auth_info, 'auth_info - from _on_signin(...)')
        if 'postloginaction' in self.session:
            postLoginAction = str(self.session['postloginaction'])
            logging.info('Doing post login action: ' + postLoginAction)            
            self.doPostLoginAction(postLoginAction, self.session)
        else:  
            target = str(self.session['original_url'])
            currentArea = self.session.get('currentArea')
            currentAreaDisplayName = self.session.get('currentAreaDisplayName')
            if target.find("/login") != -1 or currentArea:
                target = "/"
            logging.info('_ON_SIGNIN: Redirecting to %s' % target)
            self.redirect(target)
        
    
    def doPostLoginAction(self, postLoginAction, sessionData ):
        if postLoginAction == "createFromMain":
            user = self.current_user
            pointText = str(sessionData['pointtext'])
            if user:
                newPoint, newPointRoot = Point.create(
                    title=pointText,
                    content="",
                    summaryText="",
                    user=user,
                    imageURL=None,
                    imageAuthor=None,
                    imageDescription=None,
                    sourceURLs=[],
                    sourceNames=[])
                if newPoint:    
                    template_values = {
                        'user': user, 
                        'currentArea':self.session.get('currentArea'),
                        'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                        'pointURL':newPoint.url
                    }
                    html = self.template_render('waitingPage.html', template_values)
                    self.session['postloginaction'] = None
                    self.session['pointText'] = None                    
                    self.response.out.write(html)
                    ReportEvent.queueEventRecord(user.key.urlsafe(), newPoint.key.urlsafe(), None, "Create Point")    
                else:
                   logging.error("Was not able to create point with title: " + pointText)    
                   self.redirect(str(sessionData['original_url']))
            else:
                logging.error("User was not available, and so could not create point with title: " + pointText)    
                self.redirect(str(sessionData['original_url']))
        else:
            logging.info("Unknown Post Login action " + postLoginAction)    
            self.redirect(str(sessionData['original_url']))
    

    def logout(self):
        self.session['currentArea'] = ''
        self.session['currentAreaDisplayName'] = ''
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

    def LetsEncryptHandler(self, challenge):
        self.response.headers['Content-Type'] = 'text/plain'
        responses = {
                    'bLAP0scnQVL7mDmgON63gnYS97LCLmZHxB-isJs32iw': 'bLAP0scnQVL7mDmgON63gnYS97LCLmZHxB-isJs32iw.BJK2jYfaSfQa6tzdjMsTmjOdcxj9r1aUCbuaTe2DiYM',
                    '[challenge 2]': '[response 2]'
                }
        self.response.write(responses.get(challenge, ''))
        