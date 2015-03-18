import os
import django
import constants

from google.appengine.ext.webapp import template

from authhandler import AuthHandler
from models.point import Point
from models.uservote import RelevanceVote

class TestPage(AuthHandler):
    def get(self):
        user = self.current_user
        linkType = 'supporting'
        p1, pRoot1 = Point.getCurrentByUrl('CCC')
        p2, pRoot2 = Point.getCurrentByUrl('bbb')
        
        #result, newRelevance, newVoteCount = \        
        #    user.addRelevanceVote(pRoot1.key.urlsafe(), pRoot2.key.urlsafe(), linkType, 50) 
        """newRelVote = RelevanceVote(
            parent=user.key,
            parentPointRootKey = pRoot1.key,
            childPointRootKey = pRoot2.key,
            value = 50,
            linkType=linkType)
        newRelVote.put()"""
            
        # GET THE VOTE BACK
        q = RelevanceVote.query(RelevanceVote.parentPointRootKey == pRoot1.key,
           RelevanceVote.childPointRootKey == pRoot2.key, 
           RelevanceVote.linkType == linkType)
        votes = q.fetch(20)       
        message = ""
        message = 'Got %d votes on retrieval.' % len(votes) 
        template_values = {
            'user': user,
            'message': message,            
            'currentArea':self.session.get('currentArea'),
            'currentAreaDisplayName':self.session.get('currentAreaDisplayName')    
        }
        self.response.out.write(self.template_render('message.html', template_values))        
        
