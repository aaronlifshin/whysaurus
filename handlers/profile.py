import os
import constants
import json
import logging

from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.notification import Notification
from models.whysaurususer import WhysaurusUser
from google.appengine.api import namespace_manager


class Profile(AuthHandler):
    
    def makeTemplateValues(self, user, profileUser):
        viewingOwnPage = False
        if user and profileUser.url == user.url:
            viewingOwnPage = True
        if user:
            user.getActiveNotifications()
                    
        template_values = {
            'user': self.current_user,
            'profileUser': profileUser,
            'viewingOwnPage': viewingOwnPage,            
            'createdPoints' : profileUser.getCreated(),
            'editedPoints': profileUser.getEdited(),
            'currentArea':self.session.get('currentArea')
        }
        if viewingOwnPage:
            template_values['recentlyViewed'] = profileUser.getRecentlyViewed()
            template_values['notifications'] = Notification.getAllNotificationsForUser(profileUser.key)


        return template_values

    def post(self, userURL):
        userNamespace = namespace_manager.get_namespace()        
        # USERS ARE STORED IN THE DEFAULT NAMESPACE
        namespace_manager.set_namespace('')
        user = self.current_user    
        # newName=self.request.get('userName')
        newWebsiteURL=self.request.get('userWebsite')
        newUserAreas=self.request.get('userAreas')
        newUserProfession=self.request.get('userProfession')
        newUserBios=self.request.get('userBio')
        user.update(newWebsiteURL, newUserAreas, newUserProfession, newUserBios)
        namespace_manager.set_namespace(userNamespace)        
        self.response.out.write(
            self.template_render(
                'profile.html', 
                self.makeTemplateValues(user, user))) 
            
    def get(self, userURL):
        userNamespace = namespace_manager.get_namespace()
        user = self.current_user

        # USERS ARE STORED IN THE DEFAULT NAMESPACE
        namespace_manager.set_namespace('')
        profileUser = WhysaurusUser.getByUrl(userURL)
        namespace_manager.set_namespace(userNamespace)

        if user:
            permissionToView = user.admin or user.privateArea == profileUser.privateArea 
        else:
            permissionToView = profileUser.privateArea is None or profileUser.privateArea == ''
        if profileUser and permissionToView:                                        
            self.response.out.write(
                self.template_render(
                    'profile.html', 
                    self.makeTemplateValues(user, profileUser))) 
        else:
            self.response.out.write('Could not find user: ' + userURL)

    def setArea(self):
        results = {'result': False}
        newArea = self.setUserArea(namespace_manager.get_namespace() == '')
        logging.info('NEW AREA was: %s' % newArea)
        if newArea is not None:            
            results = {'result': True, 'newArea': newArea}

        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        

        