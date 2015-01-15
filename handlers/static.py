import os
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler

class About(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('about.html', 
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                 'currentArea':self.session.get('currentArea')}))


class Help(AuthHandler):
    def get(self):      
        user = self.current_user
        if user:
            user.getActiveNotifications()  
        self.response.out.write(
            self.template_render('help.html', 
                {'user': user, 
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))


class Contact(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('contact.html',
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))

class Manifesto(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('manifesto.html',
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))
                
class Education(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('education.html',
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))
                
class CommonCore(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('commonCore.html',
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))
 
class APUSH(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('apushistory.html',
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))

class Walkthrough(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('walkthrough.html',
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))
                               
class ListSignUp(AuthHandler):
    def get(self):
        user = self.current_user
        if user:
            user.getActiveNotifications()
        self.response.out.write(
            self.template_render('listSignUp.html',
                {'user': user,
                 'currentAreaDisplayName':self.session.get('currentAreaDisplayName'),
                'currentArea':self.session.get('currentArea')}))