import os
import logging
import re
from random import randint

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.ext.ndb import metadata

from authhandler import AuthHandler
from models.point import PointRoot
from models.point import Point
from models.point import Link
from models.privateArea import PrivateArea
from models.follow import Follow
from models.comment import Comment

from models.whysaurususer import WhysaurusUser

from google.appengine.api import search
from google.appengine.api.taskqueue import Task
from google.appengine.api import namespace_manager
    
from handlers.dbIntegrityCheck import DBIntegrityCheck

from google.appengine.api import namespace_manager


def indClearLowQualityFlags(cursor=None, num_updated=0, batch_size=250, cntUpdatedNet=0, namespace=None, namespaces=None):
    logging.info('ClearLowQuality Update: Start: %d  Batch: %d  Namespace: %s' % (num_updated, batch_size, namespace))

    if namespace:
        previous_namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace(namespace)
    else:
        previous_namespace = None

    try:
        query = Point.query()
        points, next_cursor, more = query.fetch_page(batch_size, start_cursor=cursor)

        cnt = 0
        cntSkip = 0
        cntUpdate = 0
        # for p in query.iter():
        for p in points:
            cnt += 1

            # if p.isLowQualityAdmin == False:
            #     cntSkip += 1
            #     continue
            if p.isLowQualityAdmin:
                cntUpdate += 1
            p.isLowQualityAdmin = False
            p.put()

        logging.info('ClearLowQuality Incremental: Count: %d  Updated: %d  Skipped: %d' % (cnt, cntUpdate, cntSkip))
    finally:
        if previous_namespace:
            namespace_manager.set_namespace(previous_namespace)

    # If there are more entities, re-queue this task for the next page.
    if more:
        deferred.defer(indClearLowQualityFlags,
                       cursor=next_cursor,
                       num_updated=(num_updated + cnt),
                       batch_size=batch_size,
                       cntUpdatedNet=(cntUpdatedNet + cntUpdate),
                       namespace=namespace,
                       namespaces=namespaces)
    else:
        logging.warning('ClearLowQuality Complete! - Net Updated: %d  Namespace: %s' % (cntUpdatedNet + cntUpdate, namespace))

        if namespaces and len(namespaces) > 0:
            nextNamespace = namespaces[0]
            del namespaces[0]
            logging.warning('ClearLowQuality: Next Namespace: %s  Count: %d' % (nextNamespace, len(namespaces)))
            deferred.defer(indClearLowQualityFlags,
                           cursor=None,
                           num_updated=0,
                           batch_size=batch_size,
                           cntUpdatedNet=0,
                           namespace=nextNamespace,
                           namespaces=namespaces)

def indUpdatePointsAllNamespace():
    namespaces = [namespace for namespace in metadata.get_namespaces()]
    logging.warning('%d Namespaces To Query: %s' % (len(namespaces), namespaces[0]))
    assert (namespaces[0] == "")
    if len(namespaces) == 1:
        namespaces = None
    else:
        del namespaces[0]

    indClearLowQualityFlags(namespaces=namespaces)
    
def changeUserUrl(cursor=None, num_updated=0, batch_size=250, cntUpdatedNet=0, namespace=None, namespaces=None):
    logging.info('ChangeUserUrl Update: Start: %d  Batch: %d  Namespace: %s' % (num_updated, batch_size, namespace))

    query = Point.query()
    points, next_cursor, more = query.fetch_page(batch_size, start_cursor=cursor)

    cnt = 0
    cntSkip = 0
    cntUpdate = 0
    # for p in query.iter():
    for p in points:
        cnt += 1

        if p.authorURL != 'Tom_Gratian' and p.authorURL != 'tom_gratian' and p.creatorURL != 'Tom_Gratian' and p.creatorURL != 'tom_gratian':
            continue

        logging.warning('ChangeUserUrl: Update: %s  Author -> (%s, %s)' % (p.url, p.authorName, p.authorURL))
        
        p.authorName = 'Big T'
        p.creatorName = 'Big T'
        p.put()
            
        cntUpdate += 1
        # p.isLowQualityAdmin = False
        # p.put()

    logging.info('ChangeUserUrl Incremental: Count: %d  Updated: %d  Skipped: %d' % (cnt, cntUpdate, cntSkip))
    
    # If there are more entities, re-queue this task for the next page.
    if more:
        deferred.defer(changeUserUrl,
                       cursor=next_cursor,
                       num_updated=(num_updated + cnt),
                       batch_size=batch_size,
                       cntUpdatedNet=(cntUpdatedNet + cntUpdate),
                       namespace=namespace,
                       namespaces=namespaces)
    else:
        logging.warning('ChangeUserUrl Complete! - Net Updated: %d  Namespace: %s' % (cntUpdatedNet + cntUpdate, namespace))


def callForAllPoints(pointUpdate, pointIsEligible=None,
                     cursor=None, num_updated=0, batch_size=250, cntUpdatedNet=0,
                     namespace=None, namespaces=None):
    logging.info('CallForAllPoints: Start: %d  Batch: %d Namespace: %s' % (num_updated, batch_size, namespace))

    if namespace:
        previous_namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace(namespace)
    else:
        previous_namespace = None

    try:
        query = Point.query()
        points, next_cursor, more = query.fetch_page(batch_size, start_cursor=cursor)
    
        cnt = 0
        cntUpdate = 0
        # for p in query.iter():
        for p in points:
            cnt += 1
            
            if pointIsEligible:
                if not (pointIsEligible(p)):
                    continue
    
            pointUpdate(p)
            cntUpdate += 1
    finally:
        if previous_namespace:
            namespace_manager.set_namespace(previous_namespace)
       
    # If there are more entities, re-queue this task for the next page.
    if more:
        logging.info('CallForAllPoints Incremental: Count: %d  Updated: %d' % (cnt, cntUpdate))
        
        deferred.defer(callForAllPoints,
                       pointUpdate=pointUpdate,
                       pointIsEligible=pointIsEligible,
                       cursor=next_cursor,
                       num_updated=(num_updated + cnt),
                       batch_size=batch_size,
                       cntUpdatedNet=(cntUpdatedNet + cntUpdate),
                       namespace=namespace,
                       namespaces=namespaces)
    else:
        logging.info('CallForAllPoints Complete! - Net Updated: %d' % (cntUpdatedNet + cntUpdate))

        if namespaces and len(namespaces) > 0:
            nextNamespace = namespaces[0]
            del namespaces[0]
            logging.warning('CallForAllPoints: Next Namespace: %s  Count: %d' % (nextNamespace, len(namespaces)))
            deferred.defer(callForAllPoints,
                           pointUpdate=pointUpdate,
                           pointIsEligible=pointIsEligible,
                           cursor=None,
                           num_updated=0,
                           batch_size=batch_size,
                           cntUpdatedNet=0,
                           namespace=nextNamespace,
                           namespaces=namespaces)
        else:
            logging.warning('CallForAllPoints Final Complete! - Net Updated: %d' % (cntUpdatedNet + cntUpdate))


def callForAllPointsAllNamespace(pointUpdate, pointIsEligible=None):
    namespaces = [namespace for namespace in metadata.get_namespaces()]
    logging.warning('%d Namespaces To Query: %s' % (len(namespaces), namespaces[0]))
    assert (namespaces[0] == "")
    if len(namespaces) == 1:
        namespaces = None
    else:
        del namespaces[0]

    callForAllPoints(pointUpdate, pointIsEligible, namespaces=namespaces)
   

class BatchJobs(AuthHandler):
    @staticmethod
    def singlePointUpdate(point):
        point.updateCachedValues(doPutOnUpdate=False)
        
    def dailyBatchJobs(self):
        logging.info('Running Daily Batch Jobs..')
        
        # Jobs
        callForAllPointsAllNamespace(singlePointUpdate)
        
        logging.info('Daily Batch Jobs Complete')
        
    def updateCachedValuesAll(self):
        # TODO: Gene: Merge with new batch AaronTask jobs and call across all points
        message = "Not Yet Implemented.."
        
        template_values = {
            'message': message,
            'user': self.current_user,
            'currentArea': self.session.get('currentArea')
        }
        self.response.out.write(self.template_render('message.html', template_values))
    
    def PopulateCreators(self):
        prs = PointRoot.query()
        cnt = 0
        bypassed = 0;
        for pr in prs.iter():
            updated = pr.populateCreatorUrl()
            if updated:
                # Just run one for now..
                cnt += 1
                if cnt > 250:
                    logging.warn('Populate Update Stop - Updated: %d Bypassed: %d' % (cnt, bypassed))
                    return
            else:
                bypassed += 1

        logging.warning('Populate Update Complete! - Updated: %d Bypassed: %d' % (cnt, bypassed))

    def PopulateGaids(self):
        maxCreates = 250
        bigMessage = ['Populating GA Ids']
        gaIds = []

        query = WhysaurusUser.query()
        for yUser in query.iter():
            if yUser.gaId is None:
                continue
            gaIds.append(yUser.gaId)

        bigMessage.append('Existing gaIds: %s' % (len(gaIds)))

        cntNewIds = 0
        query = WhysaurusUser.query()
        for yUser in query.iter():
            if yUser.gaId is not None:
                continue

            newId = yUser.generateUserGaid(isNewUser=False, existingGaids=gaIds)

            if newId is None:
                bigMessage.append('User %s (%s) failed generation: %s' % (yUser.name, str(yUser.auth_ids), yUser.gaId))
                continue

            yUser.put()

            bigMessage.append('User %s (%s) got gaId: %s' % (yUser.name, str(yUser.auth_ids), yUser.gaId))

            cntNewIds += 1
            if cntNewIds >= maxCreates:
                break

        bigMessage.append('Generated %s new gaIds' % (cntNewIds))

        template_values = {
            'messages': bigMessage
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/django/message.html')
        self.response.out.write(template.render(path, template_values))
        

    def UpdateUserName(self, userUrl, userName):
        maxUpdates = 1
        bigMessage = ['Populating user name (%s): %s' % (userUrl, userName)]
        
        updates = 0
        query = WhysaurusUser.query()
        for yUser in query.iter():
            if yUser.url != userUrl:
                continue
            bigMessage.append('Changing user name (%s / %s): %s' % (yUser.url, yUser.name, userName))
            yUser.name = userName
            yUser.put()
            updates += 1
            
        bigMessage.append('Users: %s' % (updates))

        template_values = {
            'messages': bigMessage
        }
        path = os.path.join(os.path.dirname(__file__), '../templates/django/message.html')
        self.response.out.write(template.render(path, template_values))

    def get(self):
        # self.PopulateGaids()
        # deferred.defer(IndClearLowQualityFlags)
        # deferred.defer(IndUpdatePointsAllNamespace)
        # self.UpdateUserName('Tom_Gratian', 'Big T')
        # ChangeUserUrl()
        self.response.write("""
            Batch Jobs Update. Check the console log for task progress.
            <a href="/">Home</a>.
            """)
