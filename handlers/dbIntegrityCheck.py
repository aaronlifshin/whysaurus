import os
import logging
import constants

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point

class DBIntegrityCheck(AuthHandler):
    def get(self):
        i = 0
        bigMessage = []
        # WHAT DO WE WANT TO CHECK?
        # Make sure every link is the same back and forth
        
        # Take every point version
        query = Point.query()
        i = 0
        for point in query.iter():
            link_val = point.key.urlsafe()
            bigMessage.append("--------  Checking Point %s: <a href=\"%s%s\">%s</a> "\
            % (point.title, constants.ADMIN_DATA_URL, link_val, point.key))
            if point.supportingPointsLastChange:
                for pointKey in point.supportingPointsLastChange:
                    if not pointKey.parent() in point.supportingPointsRoots:
                        bigMessage.append( \
                        "+++++ Missing corresponding root for supporting point %s " % point.key)
                    linkRoot = pointKey.parent().get()
                    if point.current:
                        if not point.key.parent() in linkRoot.pointsSupportedByMe:
                            linkVal = linkRoot.key.urlsafe()
                            bigMessage.append(
                            "+++++ Missing BACKLINK to supporting point Root %s in <a href=\"%s%s\">%s</a>" \
                             % (point.key.parent(), constants.ADMIN_DATA_URL, linkVal, linkRoot.pointsSupportedByMe))

                if len(point.supportingPointsLastChange) != len(point.supportingPointsRoots):
                    bigMessage.append(
                    "+++++ Length mismatch in supporting arrays. Version: %d. Roots: %d " % \
                    (len(point.supportingPointsLastChange), len(point.supportingPointsRoots)))

            if point.counterPointsLastChange:
                for pointKey in point.counterPointsLastChange:
                    if not pointKey.parent() in point.counterPointsRoots:
                        bigMessage.append(
                        "+++++ Missing corresponding root for counter point %s " \
                        % point.key)
                    linkRoot = pointKey.parent().get()
                    if point.current:
                        if not point.key.parent() in linkRoot.pointsCounteredByMe:
                            bigMessage.append(
                            "++++++ Missing BACKLINK for counter point %s in key %s" \
                             % (point.key, linkRoot.key))
                if len(point.counterPointsLastChange) != len(point.counterPointsRoots):
                    bigMessage.append(\
                    "++++++ Length mismatch in counter arrays. Version: %d. Roots: %d" % \
                    (len(point.counterPointsLastChange), len(point.counterPointsRoots)))
  
        query = PointRoot.query()
        for pointRoot in query.iter():
            linkVal = pointRoot.key.urlsafe()
            bigMessage.append("--------  Checking Root %s: <a href=\"%s%s\">%s</a> "\
            % (pointRoot.url, constants.ADMIN_DATA_URL, linkVal, pointRoot.key))
            curPoint = pointRoot.getCurrent()
            if not curPoint.current:
                bigMessage.append("+++++ Current point is not marked current!")
            pointQuery = Point.query(ancestor=pointRoot.key)
            points = pointQuery.fetch()
            bigMessage.append("-------  Checking %d point versions"% len(points))
            curCount = 0
            curURLs = ""
            for point in points:
                if point.current:
                    curCount = curCount + 1
                    curURLs = curURLs + point.key.urlsafe()+ ","
            if curCount != 1:
                bigMessage.append("++++++  Found %d points marked current. URL keys: %s"% (curCount, curURLs))
            for linkRootKey in pointRoot.pointsSupportedByMe:
                linkRoot = linkRootKey.get()
                if not linkRoot:
                    bigMessage.append("++++++  Not able to get root by link root key %s"% linkRootKey)
                    continue
                currentLinkPoint = linkRoot.getCurrent()
                if not pointRoot.key in currentLinkPoint.supportingPointsRoots:
                    versionKeyURL = currentLinkPoint.key.urlsafe()
                    logging.info("VU %s" % versionKeyURL)
                    bigMessage.append("++++++  Have supporting backlink from '" + pointRoot.url + "' to '" + \
                                      "<a href=\"" + constants.ADMIN_DATA_URL + versionKeyURL+ "\">'" + \
                                       currentLinkPoint.url + "'</a> but no link root." )
                
            for linkRootKey in pointRoot.pointsCounteredByMe:
                linkRoot = linkRootKey.get()
                currentLinkPoint = linkRoot.getCurrent()
                if not pointRoot.key in currentLinkPoint.counterPointsRoots:
                    versionKeyURL = currentLinkPoint.key.urlsafe()
                    logging.info("VU %s" % versionKeyURL)
                    bigMessage.append("++++++  Have COUNTER backlink from '" + pointRoot.url + "' to '" + \
                                      "<a href=\"" + constants.ADMIN_DATA_URL + versionKeyURL+ "\">'" + \
                                       currentLinkPoint.url + "'</a> but no link root." )

        
        template_values = {
            'messages': bigMessage
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/dbcheck.html')
        self.response.out.write(template.render(path, template_values))
