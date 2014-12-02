import os
import constants
import logging
import json
import string

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from authhandler import AuthHandler
from models.whysaurususer import WhysaurusUser
from models.privateArea import PrivateArea
from models.areauser import AreaUser
from models.whysaurusexception import WhysaurusException
from models.reportEvent import DayEventSummary
from google.appengine.api import namespace_manager


class AdminPage(AuthHandler):
    def createPrivateArea(self, newName):
        results = {'result': False}
        try:
            PrivateArea.create(newName) 
            results = {
                'result': True,
                'newNamespace': newName
            }
        except WhysaurusException as e:
            results['error'] = str(e)     
        
        return results
    
    def saveUsers(self, users):

        for user in users:
            u = WhysaurusUser.getByUrl(user['url'])
            if u:
                u.updatePrivateAreas(user['privateAreas'])
            else:
                results = {
                    'result': False, 
                    'error': "Could not find user %s. Other users may have been updated." % user['userAuthIDs']
                } 
                return results     
        
        return {'result': True}

    
    def post(self):
        
        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')

        
        results = {'result': False}
        user = self.current_user  
        
        action=self.request.get('action')
        if (action == 'createPrivateArea'):
            # Anyone can create a private area
            newName = self.request.get('privateAreaName')
            results = self.createPrivateArea(newName)
        elif (action == 'saveUsers'): 
            if user.admin:
                users = json.loads(self.request.get('newUserValues'))
                results = self.saveUsers(users)
            else:
                results['error'] = "User must be admin."
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        
        namespace_manager.set_namespace(userNamespace)   
          
    
    def get(self):
        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')
   
        user = self.current_user
        if user is None:
            self.response.out.write('Need to login.')
            return

        if not user.admin:
            self.response.out.write('User not authorized.')
            return

        queryUsr = WhysaurusUser.query().order(-WhysaurusUser.lastLogin)
        areas = PrivateArea.query()
        users = []
        i = 0
        for yUser in queryUsr.iter():
            users = users + [{'u':yUser, 'index':i, 'userKey': yUser.key.urlsafe()}]
            i = i+1
            
        paginator = Paginator(users, 25) 
        page = self.request.get('page')

        try:
            paginatedUsers = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paginatedUsers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginatedUsers = paginator.page(paginator.num_pages)

            
        template_values = {
            'user': user,
            'users': paginatedUsers,
            'areas': areas,
            'currentArea':self.session.get('currentArea')
        }

        self.response.out.write(
            self.template_render('admin.html', template_values))

        namespace_manager.set_namespace(userNamespace)  

    def uploadUserPage(self):

        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')

        
        user = self.current_user

        template_values = {
            'user': user,
            'currentArea':self.session.get('currentArea')
        }
        if user and user.admin:                
            self.response.out.write(
                self.template_render('uploadUsers.html', template_values)) 
        else:
            self.response.out.write('User not authorized. ')
            
        namespace_manager.set_namespace(userNamespace)       
        
        
    def uploadUsers(self):

        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')
        
        loggedInUser = self.current_user
        if loggedInUser and loggedInUser.admin:                    
            userNames=self.request.get('userNames')
            names = string.split(userNames, '\n')
            bigMessage = ['username,password']
            for name in names:
                username = name.strip()      
                try:
                    randomPassword = WhysaurusUser.random_password(8)
                    user = WhysaurusUser.signup(self, email=username, name=username, 
                                                password=randomPassword, website=None, areas=None, 
                                                profession=None, bio=None)
                    user.updatePrivateAreas(['Cannon_Human_Environments'])
                    bigMessage.append('%s,%s' % ( username, randomPassword))
                except WhysaurusException as e:
                    bigMessage.append('Could not create user: %s. Error was:%s' % (username, str(e)))
                
            template_values = {
                'user': loggedInUser,
                'messages': bigMessage
            }    
            self.response.out.write(
                self.template_render('message.html', template_values))   
        else:
            self.response.out.write('User not authorized. ')

        namespace_manager.set_namespace(userNamespace)               
            
    def dailyReport(self):
        user = self.current_user      
        if user and user.admin:    
            template_values = {
                'user': user,
                'dayReportTable': DayEventSummary.getReport()
            }   
            self.response.out.write(
                self.template_render('dailyReport.html', template_values))        

                
    def get_pa(self):
        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')
        
        user = self.current_user
        if user is None:
            self.response.out.write('Need to login.')
            return

        userIds = []
        queryUsrIds = AreaUser.query().filter(AreaUser.privateArea == userNamespace)
        for userArea in queryUsrIds.iter():
            userIds.append(ndb.Key(urlsafe=userArea.userKey))
                        
        queryUsr = ndb.get_multi(userIds)
        users = []
        i = 0        
        for yUser in queryUsr:
            if yUser.admin != True:
                users = users + [{'u':yUser, 'index':i, 'userKey': yUser.key.urlsafe()}]
                i = i+1

        paginator = Paginator(users, 35) 
        page = self.request.get('page')

        try:
            paginatedUsers = paginator.page(page)
        except PageNotAnInteger:
            paginatedUsers = paginator.page(1)
        except EmptyPage:
            paginatedUsers = paginator.page(paginator.num_pages)
                    
        template_values = {
            'user': user,
            'users': paginatedUsers,
            'currentArea':userNamespace
        }
        
        namespace_manager.set_namespace(userNamespace)   
        self.response.out.write(
            self.template_render('adminPrivateArea.html', template_values))
                