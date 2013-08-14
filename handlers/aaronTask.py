import os
import logging


from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from models.whysaurususer import WhysaurusUser

from google.appengine.api import search



class AaronTask(AuthHandler):
    def get(self):
        """
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        FILL EDITED AND CREATED ARRAYS ON USERS
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
        """
        bigMessage = ['STARTING THE WORK']
        users = {}
        query = Point.query()
        for point in query.iter():
            usr = WhysaurusUser.getByUrl(point.authorURL)
            pointRootKey = point.key.parent()
            if point.version == 1:
                if not pointRootKey in usr.createdPointRootKeys:
                    # usr.recordCreatedPoint(pointRootKey)
                    bigMessage.append('User %s created %s' % (usr.name, point.title))
                else:
                    bigMessage.append('User %s created %s (ALREADY RECORDED)' % (usr.name, point.title))
            else:
                users[usr.url] = usr.recordEditedPoint(point.key.parent(), False)
                bigMessage.append('User %s edited %s' % (usr.name, point.title))
                                
        for usrUrl, keys in users.iteritems():
            usr = WhysaurusUser.getByUrl(usrUrl)
            usr.editedPointRootKeys = keys
            usr.put()
            bigMessage.append('Writing OUT User %s' % usrUrl)
            
        template_values = {
            'messages': bigMessage
        }    
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))   
        
            
        """
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        GATHER AUTHOR NAMES FROM POINTS 
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
        bigMessage = ['STARTING THE WORK']
        namesMap = {
            'frankelfrankel':'frankelfrankel2',
            'Aaron Lifshin':'Aaron_Lifshin3',
            'Joshua Frankel':'Joshua_Frankel',
            'Colin Curtin':'Colin_Curtin1',
            'Masha Lifshin':'Masha_Lifshin',
            'Yuan Hou':'Yuan_Hou',
            'Anatoly Volovik':'Anatoly_Volovik',
            'Whysaurus':'Whysaurus',
            'Max Lifshin':'Max_Lifshin',
            'Gavin Guest':'Gavin_Guest1',
            'Eve Biddle':'Eve_Biddle',
            'Leva Pushkin':'Leva_Pushkin1'              
        }
        # authorNames = {}
        query = Point.query()
        for point in query.iter():
            if point.authorName in namesMap:
                bigMessage.append('Name in map: |%s|. Assigning %s' % (point.authorName, namesMap[point.authorName]))
                point.authorURL = namesMap[point.authorName]
                point.put()
            else:
                bigMessage.append(' +++++++++ Name not in map: |%s|.' % point.authorName)
            
        # for k,v in authorNames.iteritems():
        #    bigMessage.append('Name |%s|: Count %d' % (k, v))
            
        template_values = {
            'messages': bigMessage
        }    
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))   
        
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        CREATE URLS FOR USERS
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
        bigMessage = ['STARTING THE WORK']
        query = WhysaurusUser.query()
        for yUser in query.iter():
            yUser.url = WhysaurusUser.constructURL(yUser.name)
            yUser.put()
            bigMessage.append('User %s (%s) got URL %s' % (yUser.name, str(yUser.auth_ids), yUser.url))
            
        template_values = {
            'messages': bigMessage
        }    
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))   
            
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        REBUILD SEARCH INDEX 
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
        query = PointRoot.query()
        bigMessage = []
        i = 0
        doc_index = search.Index(name="points")

        for pointRoot in query.iter():                     
            doc = doc_index.get(pointRoot.key.urlsafe())
            if doc is None:
                pointRoot.getCurrent().addToSearchIndexNew()
                bigMessage.append('Added %s' % pointRoot.url)
            i = i + 1

        bigMessage.append("Insertions made: %d" % i)

        template_values = {
            'message': bigMessage
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        REMOVE SOME BAD LINKS 
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
        bigMessage = ['STARTING THE WORK']
        query = PointRoot.query()
        i = 0
        for pointRoot in query.iter():
            i = i + 1
            for linkRootKey in pointRoot.pointsSupportedByMe:
                linkRoot = linkRootKey.get()
                if not linkRoot:
                    pointRoot.pointsSupportedByMe.remove(linkRootKey)
                    pointRoot.put()
                    bigMessage.append("++++++  Removed %s from %s " % (linkRootKey, pointRoot.url))
                    
        bigMessage.append('Processed %d point roots' % i)          
        template_values = { 'message': bigMessage }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))               

                    
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        CLEAR FROM SEARCH INDEX ANYTHING THAT NO LONGER HAS A MATCHING POINT
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++                    
        bigMessage = []
        docIndex = search.Index(name="points")
        docIds = [d.doc_id for d in docIndex.get_range(limit=200, ids_only=True)]
        for docId in docIds:
            pointRoot = None
            try:
                pointRoot = ndb.Key(urlsafe=docId).get()
            except Exception as e:
                logging.info(
                    'Could not retrieve from doc ID %s. Error was: %s' % (docId, str(e)))
            if pointRoot:
                bigMessage.append("Found %s" % pointRoot.url)
            else:
                docIndex.delete(docId)
                bigMessage.append("Deleted %s" % docId)
        template_values = { 'message': bigMessage }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))               

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        REDO THE SEARCH INDEX SO THAT THE DOCID IS THE URLSAFE OF THE POINTROOT
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        query = PointRoot.query()
        bigMessage = []
        i = 0
        doc_index = search.Index(name="points")

        for pointRoot in query.iter():                     
            doc_index.delete(pointRoot.url)
            bigMessage.append('Removing %s' % pointRoot.url)
            pointRoot.getCurrent().addToSearchIndexNew()
            bigMessage.append('Added %s' % pointRoot.url)
            i = i + 1

        bigMessage.append("Insertions made: %d" % i)

        template_values = {
            'message': bigMessage
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
        
            
        MAKE ALL ROOTS HAVE A CURRENT
        
        query = PointRoot.query()
        i = 0
        for pointRoot in query.iter():            
            point = Point.query(Point.current == True, ancestor=pointRoot.key).get()
            pointRoot.current = point.key
            pointRoot.put()
            i = i+1
          
        template_values = {
            'message': "Edits made: %d" % i
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
        """