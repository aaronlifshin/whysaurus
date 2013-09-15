import os
import logging
import constants

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from models.privateArea import PrivateArea

from google.appengine.api import namespace_manager
  
class DBIntegrityCheck(AuthHandler):
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
                                 <a href=\"%s%s\">%s</a> with no BACKLINK" \
                                 % (point.url, point.version, linkType, \
                                    constants.ADMIN_DATA_URL, linkedPointURL, linkRoot.url))
                                foundError = True
                
                    if len(linkLastChange) != len(linkRoots):
                        bigMessage.append(
                        "Point: <a href=\"%s%s\">%s</a>. \
                            Length mismatch in %s arrays. \
                            Version List has: %d. Root Array has: %d " % \
                            (linkType, constants.ADMIN_DATA_URL, \
                             checkingPointURL, point.title, \
                             len(linkLastChange), \
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
                bigMessage.append("Root <a href=\"%s%s\">%s</a>: \
                Current point is not marked current" % \
                (constants.ADMIN_DATA_URL, linkVal, pointRoot.url))
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
                bigMessage.append("Root <a href=\"%s%s\">%s</a>: \
                Found %d points marked current. URL keys: %s" % \
                (constants.ADMIN_DATA_URL, linkVal, pointRoot.url, \
                 curCount, curURLs))
                foundError = True
                
            for linkType in ["supporting", "counter"]:
                linkPoints, archivedLinkPoints = \
                    pointRoot.getBacklinkCollections(linkType)
                for linkRootKey in linkPoints:
                    linkRoot = linkRootKey.get()
                    if not linkRoot:
                        bigMessage.append("Root <a href=\"%s%s\">%s</a>: \
                        Not able to get root by link root key %s" % \
                        (constants.ADMIN_DATA_URL, linkVal, pointRoot.url, \
                         linkRootKey))
                        foundError = True
                        continue
                    currentLinkPoint = linkRoot.getCurrent()
                    linkedPoints = currentLinkPoint.getLinkedPointsRootCollection(linkType)
                    if not pointRoot.key in linkedPoints:
                        versionKeyURL = currentLinkPoint.key.urlsafe()
                        bigMessage.append("Root <a href=\"%s%s\">%s</a>: \
                             Have %s backlink to ' \
                            <a href=\"%s%s\">%s</a> but no link root." % \
                            (constants.ADMIN_DATA_URL, linkVal, pointRoot.url,\
                             linkType, constants.ADMIN_DATA_URL, versionKeyURL, \
                             currentLinkPoint.title))
                        foundError = True
                           
            if not foundError:
                noErrors = noErrors + 1
            rootCount = rootCount + 1
            
        bigMessage.append( "%d roots checked. No errors detected in %d roots" % (rootCount, noErrors))        
        return bigMessage
    

    def get(self):
        bigMessage = []
        # WHAT DO WE WANT TO CHECK?
        # Make sure every link is the same back and forth
        namespaces = PrivateArea.query()
        for pa in namespaces.iter():
            bigMessage = bigMessage + self.checkNamespace(pa.name)
        bigMessage = bigMessage + self.checkNamespace('')

            
        template_values = {
            'messages': bigMessage,
            'user': self.current_user
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/dbcheck.html')
        self.response.out.write(template.render(path, template_values))
