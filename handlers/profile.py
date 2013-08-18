import os
import constants
import logging

from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.whysaurususer import WhysaurusUser
from google.appengine.api import namespace_manager


class Profile(AuthHandler):
    
    def makeTemplateValues(self, user, profileUser):
        viewingOwnPage = False
        if user and profileUser.url == user.url:
            viewingOwnPage = True
                    
        template_values = {
            'user': self.current_user,
            'profileUser': profileUser,
            'viewingOwnPage': viewingOwnPage,
            'createdPoints' : profileUser.getCreated(),
            'editedPoints': profileUser.getEdited(),
            'recentlyViewed': profileUser.getRecentlyViewed()
        }
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

        path = os.path.join(constants.ROOT, 'templates/profile.html')            
        self.response.out.write(template.render(path, self.makeTemplateValues(user, user))) 
            
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
            path = os.path.join(constants.ROOT, 'templates/profile.html')
            # self.response.headers["Pragma"]="no-cache"
            # self.response.headers["Cache-Control"]="no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
            # self.response.headers["Expires"]="Thu, 01 Dec 1994 16:00:00"
            self.response.out.write(template.render(path, self.makeTemplateValues(user, profileUser))) 
        else:
            self.response.out.write('Could not find user: ' + userURL)
