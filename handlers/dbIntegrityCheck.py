import os
import logging
import constants
import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.api import mail


from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from models.privateArea import PrivateArea
from models.timezones import PST
from google.appengine.api import namespace_manager
  
from google.appengine.api.taskqueue import Task


class DBIntegrityCheck(AuthHandler):
    
    def addMissingBacklinks(self, pointURL):
        point, pointRoot = Point.getCurrentByUrl(pointURL)
        if point:
            rootsAdded = point.addMissingBacklinks()
            message = 'Added %d missing roots to links of %s' % (rootsAdded, point.title)
        else:
            message = 'Could not find point'
        template_values = {
            'message': message,            
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))      

                                
    def cleanDeadBacklinks(self, pointURL):        
        point, pointRoot = Point.getCurrentByUrl(pointURL)
        if pointRoot:
            rootsRemoved = pointRoot.removeDeadBacklinks()
            message = 'Removed %d dead roots from %s' % (rootsRemoved, point.title)
        else:
            message = 'Could not find point'
        template_values = {
            'message': message,            
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))                                                 

    def reconcileVersionArrays(self, pointURL):
        point, pointRoot = Point.getCurrentByUrl(pointURL)
        if pointRoot:
            pointsRemoved = pointRoot.reconcileVersionArrays()
            message = 'Removed %d points from version root arrays in %s' % (pointsRemoved, point.title)
        else:
            message = 'Could not find point'
        template_values = {
            'message': message,            
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values)) 
        
    def queueNightlyTask(self):
        now = PST.convert(datetime.datetime.now())
        tomorrow = now + datetime.timedelta(days = 1)
        half_past_midnight = datetime.time(hour=7, minute=30) # PST 
        taskTime = datetime.datetime.combine(tomorrow, half_past_midnight)
        
        t = Task(url='/job/DBIntegrityCheck', method="GET", eta=taskTime)
        t.add(queue_name="dbchecker")
        
    def addDBTask(self):
        self.queueNightlyTask()
        template_values = {
            'message': 'Added task to QUEUE',
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
        self.response.out.write(template.render(path, template_values))
      
        
        
    def checkNamespace(self, areaName): 
        bigMessage = []
        noErrors = 0
        pointCount = 0
        bigMessage.append("ooooooooooooooooooooooooooooooooooooooooooooooooooo")
        bigMessage.append("          NAMESPACE: " + areaName)
        bigMessage.append("ooooooooooooooooooooooooooooooooooooooooooooooooooo")
        
        namespace_manager.set_namespace(areaName) 
        
        # Take every point version
        query = Point.query()
        for point in query.iter():
            foundError = False
            checkingPointURL = point.key.urlsafe()
            # bigMessage.append("--------  Checking Point %s: <a href=\"%s%s\">%s</a> "\
            # % (point.title, constants.ADMIN_DATA_URL, checkingPointURL, point.key))
            for linkType in ["supporting", "counter"]:
                linkRoots, linkLastChange = point.getLinkCollections(linkType)
                
                if linkLastChange:
                    for pointKey in linkLastChange:
                        # Check based on the version array
                        # 1. Every linked point in the version array 
                        #    has to have a root in the root array
                        if not pointKey.parent() in linkRoots: 
                            bigMessage.append( \
                            "Point %s. Version %d: Missing corresponding root \
                            for %s point %s " % (point.url, point.version, linkType, str(pointKey)))
                            foundError = True
                        if point.current:
                            # 2. Every linked point in the link array of a current point 
                            #    should have backlinks in the root of the linked point
                            linkRoot = pointKey.parent().get()
                            backlinks, archiveBacklinks = linkRoot.getBacklinkCollections(linkType)
                            if not point.key.parent() in backlinks:
                                linkedPointURL = linkRoot.key.urlsafe()
                                bigMessage.append(
                                "Point %s. Version %d: Has %s link to \
                                 <a href=\"/point/%s\">%s</a> with no BACKLINK" \
                                 % (point.url, point.version, linkType, \
                                     linkRoot.url, linkRoot.url))
                                foundError = True
                
                    if len(linkLastChange) != len(linkRoots):
                        bigMessage.append(
                        "Point: <a href=\"/point/%s\">%s</a>. Version %d: \
                            Length mismatch in %s arrays. \
                            Version List has: %d. Root Array has: %d " % \
                            (point.url, point.title, point.version,
                             linkType, len(linkLastChange), \
                             len(linkRoots)))
                        foundError = True                
            if not foundError:
                noErrors = noErrors + 1
            pointCount = pointCount + 1
            
        bigMessage.append( "%d points checked. No errors detected in %d points" % (pointCount, noErrors))
        
        noErrors = 0
        rootCount = 0
        query = PointRoot.query()
        for pointRoot in query.iter():
            foundError = False
            linkVal = pointRoot.key.urlsafe()
            # bigMessage.append("--------  Checking Root %s: <a href=\"%s%s\">%s</a> "\
            # % (pointRoot.url, constants.ADMIN_DATA_URL, linkVal, pointRoot.key))
            curPoint = pointRoot.getCurrent()
            if not curPoint.current:
                bigMessage.append("Root <a href=\"/point/%s\">%s</a>: \
                Current point is not marked current" % \
                (pointRoot.url, curPoint.title))
                foundError = True

            pointQuery = Point.query(ancestor=pointRoot.key)
            points = pointQuery.fetch()
            curCount = 0
            curURLs = ""
            for point in points:
                if point.current:
                    curCount = curCount + 1
                    curURLs = curURLs + point.key.urlsafe()+ ","
            if curCount != 1:
                bigMessage.append("Root <a href=\"/point/%s\">%s</a>: \
                Found %d points marked current. URL keys: %s" % \
                (pointRoot.url, pointRoot.url, \
                 curCount, curURLs))
                foundError = True
                
            for linkType in ["supporting", "counter"]:
                linkPoints, archivedLinkPoints = \
                    pointRoot.getBacklinkCollections(linkType)
                for linkRootKey in linkPoints:
                    linkRoot = linkRootKey.get()
                    if not linkRoot:
                        bigMessage.append("Root <a href=\"/point/%s\">%s</a>: \
                        Not able to get %s backlink root by link root key %s" % \
                        ( pointRoot.url, pointRoot.url, \
                         linkType, linkRootKey))
                        foundError = True
                        continue
                    currentLinkPoint = linkRoot.getCurrent()
                    linkedPoints = currentLinkPoint.getLinkedPointsRootCollection(linkType)
                    if not pointRoot.key in linkedPoints:
                        versionKeyURL = currentLinkPoint.key.urlsafe()
                        bigMessage.append("Root <a href=\"/point/%s\">%s</a>: \
                             Have %s backlink to ' \
                            <a href=\"%s%s\">%s</a> but no link root." % \
                            ( pointRoot.url, pointRoot.url,\
                             linkType, currentLinkPoint.url, \
                             currentLinkPoint.title))
                        foundError = True
                           
            if not foundError:
                noErrors = noErrors + 1
            rootCount = rootCount + 1
            
        bigMessage.append( "%d roots checked. No errors detected in %d roots" % (rootCount, noErrors))        
        return bigMessage
    

    def get(self):
        mode = self.request.get('mode')     

        bigMessage = []
        
        namespace_manager.set_namespace('') 
        namespaces = PrivateArea.query()
        for pa in namespaces.iter():
            logging.info("Looking at private area: " + pa.name)
            bigMessage = bigMessage + self.checkNamespace(pa.name)
        bigMessage = bigMessage + self.checkNamespace('')
         
        template_values = {
            'messages': bigMessage,
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
                

        if mode and mode == 'screen':
            path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
            self.response.out.write(template.render(path, template_values))
        else:
            path = os.path.join(os.path.dirname(__file__), '../templates/dbcheck.html')
            mail.send_mail(sender='aaron@whysaurus.com',
                to='aaronlifshin@gmail.com',
                subject='Database Integrity Check Results %s' % str(PST.convert(datetime.datetime.now())),
                html=template.render(path, template_values),
                body=str(bigMessage),
                reply_to="aaron@whysaurus.com"
                )
            self.queueNightlyTask()
            template_values = {
                'message': "Sent email successfully. Queued nightly task.",
                'user': self.current_user,
                'currentArea':self.session.get('currentArea')
            }
            path = os.path.join(os.path.dirname(__file__), '../templates/message.html')
            self.response.out.write(template.render(path, template_values))
