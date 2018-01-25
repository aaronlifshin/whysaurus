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
    
    def cleanMultipleCurrent(self, pointURL):
        pointData = Point.getFullHistory(pointURL)
        lastVersion = 0
        message = ''
        logging.info(pointData)
        if pointData:
            # Find the maximum version
            for fullPoint in pointData:
                point = fullPoint['point']
                if point.version > lastVersion:
                    lastVersion = point.version
            message = message + 'Last Version is %d. ' % lastVersion

            # Set anything that is not the maximum version to be not current
            pointsCleaned = 0
            for fullPoint in pointData:
                point = fullPoint['point']                
                if point.version < lastVersion:
                    logging.info('V %d ' % point.version)                    
                    if point.current:                        
                        point.current = False
                        point.put()
                        pointsCleaned = pointsCleaned + 1
                elif point.version == lastVersion:
                    point.current = True
                    point.put()
                    
            message = message + 'Updated to turn off current on %d versions' % pointsCleaned
        else:
            message = 'Unable to retrieve history'
                
        template_values = {
            'message': message,            
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        self.response.out.write(self.template_render('message.html', template_values))                            
    
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
        self.response.out.write(self.template_render('message.html', template_values))                    

                                
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
        self.response.out.write(self.template_render('message.html', template_values))        
                                                 

    def cleanEmptyLinks(self, pointURL):
        point, pointRoot = Point.getCurrentByUrl(pointURL)
        if pointRoot:
            linksRemoved, versionCount = pointRoot.cleanEmptyLinks()
            message = 'Removed %d dead links from structured link arrays in %d versions of %s' % \
                (linksRemoved, versionCount, point.title)
        else:
            message = 'Could not find point'
        template_values = {
            'message': message,            
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        self.response.out.write(self.template_render('message.html', template_values))        
        
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
        self.response.out.write(self.template_render('message.html', template_values))                
      
    def checkPointNew(self, point):
        try:
            retVal = False
            messages = []
            for linkType in ["supporting", "counter"]:
                links = point.getStructuredLinkCollection(linkType)   
                if links and point.current:
                    for link in links:
                        # Check the roots of points we link to for backlinks
                        linkRoot = link.version.parent().get()
                        backlinks, archiveBacklinks = linkRoot.getBacklinkCollections(linkType)
                        if not point.key.parent() in backlinks:
                            linkedPointURL = linkRoot.key.urlsafe()
                            messages.append(
                            "Point %s. Version %d: Has %s link to \
                             <a href=\"/point/%s\">%s</a> with no BACKLINK" \
                             % (point.url, point.version, linkType, \
                                 linkRoot.url, linkRoot.url))
                            retVal = True
            return retVal, messages
        except Exception as e:
            errMsg = 'Exception %s when checking %s' % (point.url, str(e))
            return True, messages + [errMsg]                                            
        
   
    
    def checkRoot(self, pointRoot): 
        try:
            foundError = False
            messages = []
            # linkVal = pointRoot.key.urlsafe()
            # bigMessage.append("--------  Checking Root %s: <a href=\"%s%s\">%s</a> "\
            # % (pointRoot.url, constants.ADMIN_DATA_URL, linkVal, pointRoot.key))
            curPoint = pointRoot.getCurrent()
            if not curPoint:
                messages.append("Not able to get current from <a href=\"/point/%s\">%s</a>. " % \
                (pointRoot.url, pointRoot.url))
                foundError = True
            elif not curPoint.current:
                messages.append("Root <a href=\"/point/%s\">%s</a>: \
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
                messages.append("Root <a href=\"/point/%s\">%s</a>: \
                Found %d points marked current. URL keys: %s" % \
                (pointRoot.url, pointRoot.url, \
                 curCount, curURLs))
                messages.append('<a href=\"/job/cleanCurrents/%s\"> \
                    Clean multiple current points</a>' % pointRoot.url)
                foundError = True
                
            for linkType in ["supporting", "counter"]:
                linkPoints, archivedLinkPoints = \
                    pointRoot.getBacklinkCollections(linkType)
                for linkRootKey in linkPoints:
                    linkRoot = linkRootKey.get()
                    if not linkRoot:
                        messages.append("Root <a href=\"/point/%s\">%s</a>: \
                        Not able to get %s backlink root by link root key %s" % \
                        ( pointRoot.url, pointRoot.url, \
                         linkType, linkRootKey))
                        foundError = True
                        continue
                    currentLinkPoint = linkRoot.getCurrent()
                    linkedPoints = currentLinkPoint.getLinkedPointsRootKeys(linkType)
                    if not pointRoot.key in linkedPoints:
                        versionKeyURL = currentLinkPoint.key.urlsafe()
                        messages.append("Root <a href=\"/point/%s\">%s</a>: \
                             Have %s backlink to ' \
                            <a href=\"%s%s\">%s</a> but no link root." % \
                            ( pointRoot.url, pointRoot.url,\
                             linkType, currentLinkPoint.url, \
                             currentLinkPoint.title))
                        foundError = True  
            return foundError, messages
        except Exception as e:
            errMsg = 'Exception %s when checking %s' % (pointRoot.url, str(e))
            return True, messages + [errMsg]
    
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
            foundError, newMessages = self.checkPoint(point)   
            bigMessage = bigMessage + newMessages      
            if not foundError:
                noErrors = noErrors + 1
            pointCount = pointCount + 1
            
        bigMessage.append( "%d points checked. No errors detected in %d points" % (pointCount, noErrors))
        
        noErrors = 0
        rootCount = 0
        query = PointRoot.query()
        for pointRoot in query.iter():
            foundError, newMessages = self.checkRoot(pointRoot)
            bigMessage = bigMessage + newMessages
                      
            if not foundError:
                noErrors = noErrors + 1
            rootCount = rootCount + 1
            
        bigMessage.append( "%d roots checked. No errors detected in %d roots" % (rootCount, noErrors))        
        return bigMessage
    
    def checkDBPoint(self, pointURL):
        point, pointRoot = Point.getCurrentByUrl(pointURL)
        
        if point:
            isError1, messages1 = self.checkPointNew(point)
            
        if pointRoot:
            isError2, messages2 = self.checkRoot(pointRoot)
        
        if not isError1 and not isError2:
            message = 'No errors were found.'
        else:
            messages = []
            if messages1:
                messages += messages1
            if messages2:
                messages += messages2
            if messages == []:
                messages = ['Errors generated, but no messages generated.']
            
        template_values = {
            'messages': messages,            
            'user': self.current_user,
            'currentArea':self.session.get('currentArea')
        }
        self.response.out.write(self.template_render('message.html', template_values))        
      
        
    
    # This method is a static method so that it cat be used inside of pointRootsMap
    #   (see AaronTask.py)
    @staticmethod
    def checkDBPointRoot(pointRoot):
        logging.info('Checking %s ' % pointRoot.url)
        point, pr = Point.getCurrentByUrl(pointRoot.url)
        isError1 = False
        isError2 = False
        messages1 = []
        messages2 = []
        
        dbc = DBIntegrityCheck()
        if point:
            isError1, messages1 = dbc.checkPoint(point)
            
        if pointRoot:
            isError2, messages2 = dbc.checkRoot(pointRoot)
        
        if not isError1 and not isError2:
            message = 'No errors were found in %s.' % pointRoot.url
            logging.info(message)                      
            
        else:
            message = []
            if messages1:
                message = message + messages1
            if messages2:
                message = message + messages2
            if message == []:
                message = ['Errors generated, but no messages generated.']
            if isError1:
                logging.info(messages1)
            if isError2:
                logging.info(messages2)  
            for m in message:
                logging.info(message)                      
        
        return message


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
            self.response.out.write(self.template_render('message.html', template_values))                    
        else:
            path = os.path.join(os.path.dirname(__file__), '../templates/dbcheck.html')
            
            # old version, delete once the new version is working:            
            # mail.send_mail(sender='aaron@whysaurus.com',
            #    to='aaronlifshin@gmail.com',
            #    subject='Database Integrity Check Results %s' % str(PST.convert(datetime.datetime.now())),
            #    html=template.render(path, template_values),
            #    body=str(bigMessage),
            #    reply_to="aaron@whysaurus.com"
            #    )
                
            # new version:
            message = mail.EmailMessage(
                sender='aaron@whysaurus.com',
                        to='aaronlifshin@gmail.com',
                        cc='joshua@whysaurus.com',
                        subject='Database Integrity Check Results %s' % str(PST.convert(datetime.datetime.now())),
                        body=str(bigMessage),
                        reply_to="aaron@whysaurus.com"
                )                    
                if html:
                    message.html = template.render(path, template_values),
                message.send()
            # (end of new version)                    
                
            self.queueNightlyTask()
            template_values = {
                'message': "Sent email successfully. Queued nightly task.",
                'user': self.current_user,
                'currentArea':self.session.get('currentArea')
            }
            self.response.out.write(self.template_render('message.html', template_values))        
            
