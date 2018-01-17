import re
import time
import logging
import random
import string
import datetime
import webapp2
from random import randint

from google.appengine.ext import ndb
from google.appengine.api import search
import webapp2_extras.appengine.auth.models as auth_models
from webapp2_extras.appengine.auth.models import Unique

from webapp2_extras import security
from google.appengine.api import namespace_manager
from google.appengine.api import mail
from google.appengine.api import channel
#from google.cloud import error_reporting

from models.notification import Notification
from models.chatUser import ChatUser
from models.point import getCurrent_async
from models.areauser import AreaUser

from whysaurusexception import WhysaurusException
from uservote import UserVote
from uservote import RelevanceVote
from timezones import PST

from models.reportEvent import ReportEvent


class WhysaurusUser(auth_models.User):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    url = ndb.StringProperty(default=None)
    gaId = ndb.StringProperty(default=None)
    numCopies = ndb.IntegerProperty(default=0)
    admin = ndb.BooleanProperty(default=False)
    role = ndb.StringProperty(default="")
    recentlyViewedRootKeys = ndb.KeyProperty(repeated=True)
    viewCount = ndb.IntegerProperty(default=0)
    lastViewed = ndb.DateTimeProperty()
    lastVisitDate = ndb.DateTimeProperty()
    lastVisitCount = ndb.IntegerProperty(default=0)
    lastVisitAvgIntervalDays = ndb.FloatProperty(default=0)
    createdPointRootKeys = ndb.KeyProperty(repeated=True)
    editedPointRootKeys = ndb.KeyProperty(repeated=True)
    websiteURL = ndb.StringProperty()
    areasOfExpertise = ndb.StringProperty()
    currentProfession = ndb.StringProperty()
    bio = ndb.StringProperty()
    # TODO; take out once migrated to privateAreas
    privateArea = ndb.StringProperty()
    privateAreas = ndb.StringProperty(repeated=True)
    password = ndb.StringProperty()
    token = ndb.StringProperty()  
    tokenExpires = ndb.DateTimeProperty()
    lastLogin = ndb.DateTimeProperty()
    loginCount = ndb.IntegerProperty(default=0)
    loginAvgIntervalDays = ndb.FloatProperty(default=0)
    notificationFrequency = ndb.StringProperty(default="Weekly")
    lastEmailSent = ndb.DateTimeProperty()
    _notifications = None
    
    # linkedInProfileLink = ndb.StringProperty()
    # facebookProfileLink =  ndb.StringProperty()
    # googleProfileLink =  ndb.StringProperty()
    # twitterProfileLink =  ndb.StringProperty()

    @property
    def PSTupdated(self):
        return PST.convert(self.updated)
    
    @property
    def PSTlastlogin(self):
        return PST.convert(self.lastLogin)

    @property
    def PSTlastView(self):
        return PST.convert(self.lastViewed)
        
    @property
    def notifications(self):
        return self._notifications
    
    @property
    def newNotificationCount(self):
        return self._newNotificationCount
 
    @property
    def moreNotificationsExist(self):
        return self._moreNotificationsExist
        
    @property
    def isTeacher(self):
        return self.role == "Teacher"
        
    @property
    def isLimited(self):
        return self.role == "Limited"

    @property
    def isAdmin(self):
        return self.admin or (self.role == 'Admin')
       
    def getActiveNotifications(self):
        self._notifications, self._newNotificationCount, \
            self._moreNotificationsExist = \
                Notification.getLatestNotificationsForUser(self.key)
        return self._notifications

    def getUnreadNotifications(self):
        self._notifications, self._newNotificationCount, \
            self._moreNotificationsExist = \
                Notification.getUnreadNotificationsForUser(self.key)
        return self._notifications
        
    def getUnreadNotificationsAfter(self, afterDate):
        self._notifications, self._newNotificationCount, \
            self._moreNotificationsExist = \
                Notification.getUnreadNotificationsForUserAfterDate(self.key, afterDate)
        return self._notifications

    # A small subset of user stuff to store the relevant information for chat
    def makeChatUser(self):
        return ChatUser(parent = self.key,
                        token = self.token,
                        tokenExpires=self.tokenExpires,
                        )

    def clearNotifications(self, latest, earliest=None):
        Notification.clearNotifications(self.key, latest, earliest)

    def filterKeylistByCurrentNamespace(self, keylist):        
        currentNamespace = namespace_manager.get_namespace()        
        return filter(lambda key: key.namespace() == currentNamespace, keylist)            

    def set_password(self, raw_password):
        """Sets the password for the current user
        
        :param raw_password:
            The raw password which will be hashed and stored
        """
        self.password = security.generate_password_hash(raw_password, length=12)

    def resetPassword(self):
        randomPassword = WhysaurusUser.random_password(8)
        self.set_password(randomPassword)
        self.put()
        return randomPassword


    def setUserGaid(self, newGaid):
        self.gaId = newGaid
        self.put()
        return newGaid

    def generateUserGaid(self, isNewUser, existingGaids = None):
        """Generate (but don't put) a unique GA Id for the user (can be long running!)"""

        if self.gaId is not None:
            return self.gaId

        newId = WhysaurusUser.generateUniqueUserGaid(isNewUser, existingGaids)

        self.gaId = newId

        return newId

    @staticmethod
    def generateUniqueUserGaid(isNewUser, existingGaids = None):
        # Obviously a bit excessive to query all users - should we switch to something more heuristic?
        if existingGaids is None:
            existingGaids = []
            query = WhysaurusUser.query()
            for yUser in query.iter():
                if yUser.gaId is None:
                    continue
            existingGaids.append(yUser.gaId)

        newId = None

        cntAttempts = 0
        while True:
            cntAttempts += 1
            if cntAttempts > 100:
                logging.error('Too Many Attempts To Generate Unique GA Id!')
                return None

            if isNewUser:
                newId = datetime.datetime.now().strftime("%y%m%d%H") + str(randint(100, 10000))
            else:
                newId = str(randint(10000, 1000000))
            if id in existingGaids:
                continue
            else:
                break

        if newId is None:
            return None

        return newId
    
    def login(self):
        now = datetime.datetime.now()
        if self.lastLogin:
            daysSinceLastLogin = (now - self.lastLogin).days
            self.loginAvgIntervalDays = (daysSinceLastLogin + self.loginAvgIntervalDays * self.loginCount)/(self.loginCount + 1)
            self.loginCount += 1
        # Update last login time
        self.lastLogin = now
        # Create And Store Token    
        if not self.token or self.tokenExpires < now: 
            self.createChannel()                 
        self.put()
        
        ReportEvent.queueEventRecord(self.key.urlsafe(), None, None, "Login")    
                        
        return
    
    def createChannel(self, saveUser=False):
        now = datetime.datetime.now()
        self.token = channel.create_channel(self.url, duration_minutes=1440)
        self.tokenExpires = now + datetime.timedelta(days=1)
        logging.info('Creating new token for user %s: %s' % (self.url, self.token))        
        if saveUser:
            self.put()
        return self

    # OMG Django I hate you so much
    @property
    def anyPrivateAreas(self):
        return len(self.privateAreas) > 0

    @property
    def manyPrivateAreas(self):
        return len(self.privateAreas) > 1

    @classmethod
    def signup(cls, handler, email, name, password, website, areas, profession, bio):
                   
        auth_id = '%s: %s' % ('name', name)
        url = WhysaurusUser.constructURL(name)
        gaid = WhysaurusUser.generateUniqueUserGaid(True)
    
        unique_properties = ['email', 'url', 'name'] if email else ['url', 'name']
        
        if password is None:
            raise WhysaurusException('Unable to create user. No password supplied.')

        privateAreas = []
        existingPrivateArea = handler.session.get('currentArea')
        if existingPrivateArea:
            privateAreas = [existingPrivateArea]

        result, creationData = WhysaurusUser.create_user(auth_id,
          unique_properties,
          url=url, email=email, name=name, password_raw=password, gaId=gaid,
          websiteURL=website, areasOfExpertise=areas, currentProfession=profession, 
          bio=bio, verified=False, privateAreas=privateAreas)
 
        if not result: #user_data is a tuple
            if 'name' in creationData:
                raise WhysaurusException('Unable to create user because the username %s is already in use' % name)
            elif 'email' in creationData:
                raise WhysaurusException('Unable to create user because the email %s is already in use' % email)
            else:
                raise WhysaurusException('Unable to create user for email %s because of \
                    duplicate keys %s' % (auth_id, user_data[1]))
        else:    
            user = creationData
            if email:
                user_id = user.get_id()
                user.auth_ids.append('%s: %s' % ('email', email))
                user.put()            
                WhysaurusUser.send_verification_email(handler, user_id, email, "signing up for Whysaurus")
                
            else:
                logging.info('Created a username only user. Name: %s.' % name)
                
            if existingPrivateArea:
                areaUser = AreaUser(userKey=user.key.urlsafe(), privateArea=existingPrivateArea)
                areaUser.putUnique()

            ReportEvent.queueEventRecord(user.key.urlsafe(), None, None, "New User")
            user.addToSearchIndex()         
            return user # SUCCESS       


    @staticmethod
    def send_verification_email(handler, user_id, email, reason):
        token = WhysaurusUser.create_signup_token(user_id)

        verification_url = handler.uri_for('verification', type='v', user_id=user_id,
                                           signup_token=token, _full=True)

        mail.send_mail(sender='Whysaurus <community@whysaurus.com>',
            to=email,
            subject='Whysaurus Email Verification',
            body="Thank you for %s. \n\
                Please verify your email address by navigating to this link: \
                %s\n\nThanks, \nWhysaurus" % (reason, verification_url), 
            html="Thank you for %s. <br>\
                Please verify your email address by clicking on \
                <a href=\"%s\">this link</a>.<br><br>Thanks,<br>Whysaurus<br> \
                CTO" % (reason, verification_url),                
            reply_to="community@whysaurus.com"
        )            
        logging.info('Sending verification email for %s. Email: %s. Verification URL was: %s' % \
            (reason, email, verification_url))

    @classmethod
    def get_by_auth_token(cls, user_id, token, subject='auth'):
        """Returns a user object based on a user ID and token.
        
        :param user_id:
            The user_id of the requesting user.
        :param token:
            The token string to be verified.
        :returns:
            A tuple ``(User, timestamp)``, with a user object and
            the token timestamp, or ``(None, None)`` if both were not found.
        """
        token_key = cls.token_model.get_key(user_id, subject, token)
        user_key = ndb.Key(cls, user_id)
        # Use get_multi() to save a RPC call.
        valid_token, user = ndb.get_multi([token_key, user_key])
        if valid_token and user:
            timestamp = int(time.mktime(valid_token.created.timetuple()))
            return user, timestamp       
        return None, None

    @classmethod
    def get_by_email(cls, email):
        qry = cls.gql("WHERE email= :1", email)
        return qry.get()
    
    @classmethod
    def get_by_name(cls, name):
        qry = cls.gql("WHERE name= :1", name)
        return qry.get()

    @classmethod
    def migrate_private_areas_cls(cls):
        q = cls.query()
        for u in q.iter():
            u.migrate_private_areas_self()

    def migrate_private_areas_self(self):
        if self.privateArea:
            self.privateAreas = [self.privateArea]
            self.put()

    @webapp2.cached_property
    def notificationFrequencyText(self):
        if self.notificationFrequency:
            return self.notificationFrequency
        else:
            return "Never"
        
    @webapp2.cached_property
    def emailUser(self):
        auth_ids = self.auth_ids
        emailUser = False
        for auth_id in auth_ids:
            if 'email' in auth_id:
                emailUser = True
                break
            elif 'name' in auth_id:
                emailUser = True
                break
        return emailUser
        
    @property
    def createdCount(self):
        return len(self.createdPointRootKeys)
 
    @property
    def editedCount(self):
        return len(self.editedPointRootKeys)

    @property
    def viewedCount(self):
        if self.viewCount and self.viewCount > len(self.recentlyViewedRootKeys):
            return self.viewCount
        return len(self.recentlyViewedRootKeys)

    def getVoteFuture(self, pointRootKey):
        return UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get_async()

    @ndb.tasklet
    def getVote_async(self, pointRootKey):
        vote = yield UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get_async()
        raise ndb.Return(vote)
        
    def getVoteValue(self, pointRootKey):
        vote = UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get()
        return vote.value if vote else 0

    @ndb.tasklet
    def getVoteValue_async(self, pointRootKey):
        vote = yield UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get_async()
        raise ndb.Return(vote.value if vote else 0)
        
    def getVoteValues(self, pointRootKey):
        vote = UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get()
        if vote:
            return vote.value, vote.ribbon
        else:
            return 0, False                    

    def updateUserSettings(self, pas, role = None):
        oldPas = AreaUser.query(AreaUser.userKey==self.key.urlsafe()).fetch()
        
        for y in oldPas:
            if y.privateArea not in pas:
                y.deleteRelationship()
     
        for x in pas:
            areaUser = AreaUser(userKey=self.key.urlsafe(), privateArea=x)
            areaUser.putUnique()
            
        if role:
          self.role = role

        self.privateAreas = pas
        self.put()            

    def _getOrCreateVote(self, pointRootKey):
        vote = UserVote.query(             
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get()            
        if not vote:  # No vote yet, create a new one
            vote = UserVote(
                pointRootKey=pointRootKey,
                value=0,
                ribbon=False,
                parent=self.key
            )        
        return vote
        
    def addVote(self, point, voteValue, updatePoint=True):
        pointRootKey = point.key.parent()
        vote = self._getOrCreateVote(pointRootKey)
        previousVoteValue = vote.value
        vote.value = voteValue
        vote.put()
        
        # We only send notifications for agrees at the moment
        if voteValue == 1:
            point.addNotificationTask(pointRootKey, self.key, 1)
        # elif voteValue == -1:
        #     point.addNotificationTask(pointRootKey, self.key, 8)
        # else:
        #     logging.warning('Unexpected Vote Value For Notification: %d' % voteValue)

        if updatePoint:
            if previousVoteValue == 0 and voteValue == 1:  # UPVOTE
                point.upVotes = point.upVotes + 1
            if previousVoteValue == 0 and voteValue == -1:  # DOWNVOTE
                point.downVotes = point.downVotes + 1
            if previousVoteValue == 1 and voteValue == 0:  # CANCEL UPVOTE
                point.upVotes = point.upVotes - 1
            if previousVoteValue == -1 and voteValue == 0:  # CANCEL DOWNVOTE
                point.downVotes = point.downVotes - 1
            if previousVoteValue == -1 and voteValue == 1:  # DOWN TO UP
                point.downVotes = point.downVotes - 1
                point.upVotes = point.upVotes + 1
            if previousVoteValue == 1 and voteValue == -1:  # UP TO DOWN
                point.downVotes = point.downVotes + 1
                point.upVotes = point.upVotes - 1
            point.voteTotal = point.upVotes - point.downVotes
            point.put()

        return vote

    def setRibbon(self, point, ribbonValue, updatePoint=True):
        pointRootKey = point.key.parent()
        vote = self._getOrCreateVote(pointRootKey)
        previousRibbon = vote.ribbon
        vote.ribbon = ribbonValue            
        vote.put() 
        if updatePoint:
            if not previousRibbon and ribbonValue:
                point.ribbonTotal = point.ribbonTotal + 1
                point.put()
            elif previousRibbon and not ribbonValue:
                point.ribbonTotal = point.ribbonTotal - 1
                point.put()
                
        # Only send a notification if a ribbnon is awarded
        if ribbonValue:
            point.addNotificationTask(pointRootKey, self.key, 2)

        return vote
            
    def addRelevanceVote(self, parentRootURLsafe, childRootURLsafe, linkType, vote):
        parentRootKey = ndb.Key(urlsafe=parentRootURLsafe)
        childRootKey = ndb.Key(urlsafe=childRootURLsafe)
        pointRoot = parentRootKey.get()
        curPoint = pointRoot.current.get()
        
        oldRelVote = RelevanceVote.query(
            RelevanceVote.parentPointRootKey == parentRootKey,
            RelevanceVote.childPointRootKey == childRootKey,
            RelevanceVote.linkType == linkType,
            ancestor=self.key).get()
            
        newRelVote = RelevanceVote(
            parent=self.key,
            parentPointRootKey = parentRootKey,
            childPointRootKey = childRootKey,
            value = vote,
            linkType=linkType)
        return self.transactionalAddRelevanceVote(
            curPoint, oldRelVote, newRelVote)
        
    def getRelevanceVotes(self, parentPoint):
        parentRootKey = parentPoint.key.parent();
        maxNumVotes = parentPoint.numSupporting + parentPoint.numCounter;
        
        rVotes = None
        if maxNumVotes > 0:
            # MULTIPLY numVotes * 2 because the current set of points may be smaller
            # than the set for a given version
            rVotes = RelevanceVote.query(
                RelevanceVote.parentPointRootKey == parentRootKey, 
                ancestor = self.key).fetch(maxNumVotes*2)
        return rVotes

    @ndb.tasklet
    def getRelevanceVotes_async(self, parentPoint):
        parentRootKey = parentPoint.key.parent();
        maxNumVotes = parentPoint.numSupporting + parentPoint.numCounter;
        
        rVotes = None
        if maxNumVotes > 0:
            # MULTIPLY numVotes * 2 because the current set of points may be smaller
            # than the set for a given version
            rVotes = yield RelevanceVote.query(
                RelevanceVote.parentPointRootKey == parentRootKey, 
                ancestor = self.key).fetch_async(maxNumVotes*2)
        raise ndb.Return(rVotes)
        
    
    # Returns: true/false, new vote value, new number of votes on this line 
    @ndb.transactional(xg=True)
    def transactionalAddRelevanceVote(self, parentPoint, oldRelVote, newRelVote):
        # This will write to the point version's link array
        try: 
            result, newRelevance, voteCount = parentPoint.addRelevanceVote(
                oldRelVote, newRelVote)
            if result:                
                if oldRelVote:
                    # Update the user's vote for this link
                    oldRelVote.value = newRelVote.value
                    oldRelVote.put()
                    logging.info('TARV: Updating existing vote.')
                else:
                    logging.info('TARV: Adding new vote.')
                    newRelVote.put()
                return True, newRelevance, voteCount
        except Exception as e:
            logging.exception('Could not write to NDB during transactionalAddRelevanceVote')
            return False, None, None
        

            

    def _updateRecentlyViewed(self, pointRootKey):
        addedToList = False

        if not self.recentlyViewedRootKeys:
            self.recentlyViewedRootKeys = [pointRootKey]
            addedToList = True

        if pointRootKey in self.recentlyViewedRootKeys:
            self.recentlyViewedRootKeys.remove(pointRootKey)
            self.recentlyViewedRootKeys.insert(0, pointRootKey)
        else:
            self.recentlyViewedRootKeys.insert(0, pointRootKey)
            addedToList = True

        if len(self.recentlyViewedRootKeys) > 10:
            self.recentlyViewedRootKeys.pop()

        if not self.viewCount:
            self.viewCount = len(self.recentlyViewedRootKeys)
        else:
            self.viewCount += 1

        now = datetime.datetime.now()
        self.lastViewed = now

        if self.lastVisitDate:
            if self.lastVisitDate.date() == now.date():
                pass
            else:
                daysSinceLastVisit = (now.date() - self.lastVisitDate.date()).days
                self.lastVisitAvgIntervalDays = (daysSinceLastVisit + self.lastVisitAvgIntervalDays * self.lastVisitCount) / (self.lastVisitCount + 1)
                self.lastVisitCount += 1
                self.lastVisitDate = now
        else:
            # Let's not count the very first visit so we're consistent
            self.lastVisitCount = 0
            self.lastVisitAvgIntervalDays = 0
            self.lastVisitDate = now

        # We won't put here as each call here is responsible to put afterward
        
        return addedToList

    
    def updateRecentlyViewed(self, pointRootKey):
        self._updateRecentlyViewed(pointRootKey)
        self.put_async()
        return self.recentlyViewedRootKeys
    
    def recordCreatedPoint(self, pointRootKey):
        self._updateRecentlyViewed(pointRootKey)

        if not self.createdPointRootKeys:
            self.createdPointRootKeys = [pointRootKey]
            self.put()            
        else:
            if not pointRootKey in self.createdPointRootKeys:
                self.createdPointRootKeys.insert(0, pointRootKey)
                self.put()
                            
        
    def recordEditedPoint(self, pointRootKey, write=True):
        if not self.editedPointRootKeys:
            self.editedPointRootKeys = [pointRootKey]
        else:
            if not pointRootKey in self.editedPointRootKeys:
                self.editedPointRootKeys.insert(0, pointRootKey)
            else:
                self.editedPointRootKeys.remove(pointRootKey)
                self.editedPointRootKeys.insert(0, pointRootKey)
        if write:
            self.put()
        return self.editedPointRootKeys


    def getRecentlyViewed(self, excludeList=None):
        recentlyViewedPoints = []
        keysToGet = self.filterKeylistByCurrentNamespace(self.recentlyViewedRootKeys)
        if excludeList:
            for x in excludeList:
                try:
                    keysToGet.remove(x)
                except ValueError:
                    pass
        pointRoots = ndb.get_multi(keysToGet)
        for pointRoot in pointRoots:
            if pointRoot:
                recentlyViewedPoints = recentlyViewedPoints + [
                    pointRoot.getCurrent()]
        return recentlyViewedPoints
    
    @ndb.tasklet
    def getRecentlyViewed_async(self, excludeList=None):
        recentlyViewedPoints = []
        keysToGet = self.filterKeylistByCurrentNamespace(self.recentlyViewedRootKeys)
        if excludeList:
            for x in excludeList:
                try:
                    keysToGet.remove(x)
                except ValueError:
                    pass
        recentlyViewedPoints = yield map(lambda x: getCurrent_async(x), (yield ndb.get_multi_async(keysToGet)))
        raise ndb.Return(recentlyViewedPoints)             
        
    def getCreated(self):
        createdPoints = []
        # logging.info("Create point root keys: %d" % len(self.createdPointRootKeys))
        rootKeys = self.filterKeylistByCurrentNamespace(self.createdPointRootKeys)
        # logging.info("Filtered root keys by %s: %d" %  \
        #    (namespace_manager.get_namespace(), len(rootKeys)))
        # logging.info("Root key list " + str(rootKeys))
        pointRoots = ndb.get_multi(rootKeys[0:50])
        for pointRoot in pointRoots:
            if pointRoot:
                createdPoints = createdPoints + [pointRoot.getCurrent()]
        return createdPoints
        

    def getEdited(self):
        editedPoints = []
        rootKeys = self.filterKeylistByCurrentNamespace(self.editedPointRootKeys)
        pointRoots = ndb.get_multi(rootKeys[0:50])
        for pointRoot in pointRoots:
            if pointRoot:
                editedPoints = editedPoints + [pointRoot.getCurrent()]
        return editedPoints
    
    def update(self, handler, newWebsiteURL, newUserAreas, newUserProfession, newUserBio, newEmail, newNotificationFrequency):
        # self.name = newName if newName.strip() != "" else None
        self.websiteURL =  newWebsiteURL if newWebsiteURL.strip() != "" else None
        self.areasOfExpertise = newUserAreas if newUserAreas.strip() != "" else None
        self.currentProfession = newUserProfession if newUserProfession.strip() != "" else None
        self.bio = newUserBio if newUserBio.strip() != "" else None
        self.notificationFrequency = newNotificationFrequency if newNotificationFrequency.strip() != "" else None
        if newEmail != self.email:
            new_auth_id = '%s: %s' % ('email', newEmail)            
            # Make sure that email is unique
            success = Unique.create(new_auth_id)                                
            if success:    
                if (self.emailUser):
                    # Replace the email in the auth ID array
                    new_auth_ids = [x for x in self.auth_ids if not 'email' in x]
                    new_auth_ids.append(new_auth_id)
                    self.auth_ids = new_auth_ids
                # send a validation email 
                WhysaurusUser.send_verification_email(
                    handler, 
                    self.get_id(), 
                    newEmail, 
                    "updating your email address")
                self.email = newEmail if newEmail.strip() != "" else None
                # I should only update index if email is changed, so this is theoretically 
                # the right place, but what if put later fails?
                self.addToSearchIndex()            
            else:
                raise WhysaurusException("The email address %s already exists" % newEmail)                       
        self.put()
        
    @staticmethod
    def constructURL(name):
        userURL = name.replace(" ", "_")
        userURL = re.sub('[\W]+', '', userURL)
        # Check if it already exists
        userQuery = WhysaurusUser.gql("WHERE url= :1", userURL)
        existingUser = userQuery.get()
    
        if existingUser:
            # Existing URL notes how many URLs+number exist for that URL
            existingUser.numCopies = existingUser.numCopies + 1
            userURL = userURL + str(existingUser.numCopies)
            existingUser.put()
        return userURL
            
    @staticmethod
    def getByUrl(url):
        #logging.info('Method getByUrl URL=%s' % url)
        qry = WhysaurusUser.gql("WHERE url= :1", url)
        return qry.get()

    @staticmethod
    def random_password(length=8):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        password = ''
        for i in range(length):
            password += random.choice(chars)
        return password

    def clearLastEmailed(self):
        self.lastEmailSent = None
        self.put()

    def canSendUserEmail(self):
        # TODO: Should we check that we haven't sent to many emails to the user, etc?
        return hasattr(self, 'email') and self.email

    def sendUserEmail(self, subject, body, html):
        if not self.canSendUserEmail():
            raise RuntimeError('User.canSendUserEmail failed for sent request')

        message = mail.EmailMessage(
            sender='Whysaurus <community@whysaurus.com>',
            to=self.email,
            bcc='notification.copies@whysaurus.com',
            subject=subject,
            body=body,
            reply_to="community@whysaurus.com"
        )

        if html:
            message.html = html

        message.send()

    def sendUserNotificationEmailTest(self):
        user = self
        # try:
        lastSentTime = user.lastEmailSent if user.lastEmailSent else datetime.datetime(2000, 1, 1)
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        lastDaySent = datetime.datetime(lastSentTime.year, lastSentTime.month, lastSentTime.day)
        timeDelta = today - lastDaySent
        daysDiff = timeDelta.days

        shouldEmail = False

        if user.email == 'eebyrne@ymail.com':
            shouldEmail = True
        elif user.notificationFrequency == "Daily" and daysDiff >= 1:
            shouldEmail = True
        elif user.notificationFrequency == "Weekly" and daysDiff >= 7:
            shouldEmail = True

        if shouldEmail:
            if not user.canSendUserEmail():
                logging.info('User %s has unread notifications but email unavailable' % user.name)
                return

            logging.info('Checking for active notifications for user %s' % user.name)
            notifications = user.getUnreadNotificationsAfter(lastSentTime)
            if notifications:
                logging.info('Sending %d notifications to user %s' % (len(notifications), user.name))

                # generate the email body from the notifications
                # html = handler.template_render(
                #     'notificationEmail.html',
                #     {'user': user, 'notifications': notifications}
                # )

                points = [(n.referencePoint.title if n.referencePoint else '') + '\n' for n in notifications]
                points = list(set(points))
                # text = handler.template_render(
                #     'notificationEmailText.html',
                #     {'user': user, 'pointTitles': points}
                # )
                text = 'Notification Stub for %d points' % len(points)

                self.sendUserEmail(
                    subject=user.name + ', People are reacting to your views on Whysaurus!',
                    body=text,
                    html = None
                )
                # mail.send_mail(sender='Whysaurus <community@whysaurus.com>',
                #                to=[user.email, 'notification.copies@whysaurus.com'],
                #                subject=user.name + ', People are reacting to your views on Whysaurus!',
                #                body=text,
                #                html=html,
                #                reply_to="community@whysaurus.com"
                #                )

                logging.info('Sent mail to user %s' % user.name)
                # write the time the last notification was sent
                user.lastEmailSent = datetime.datetime.now()
                user.put()

        else:
            logging.info('User %s has no unread notifications or was emailed recently' % user.name)
        # except:
        #     logging.error('Exception processing notifications for user: %s' % user.name)
        #     # TODO: Support full error reporting  (Needs google-cloud imports)
        #     # error_reporting.Client().report_exception()
        #     return

    @classmethod
    def sendNotificationEmails(cls, handler):
        # retrieve and iterate all users where the frequency is daily or weekly
        cntErrors = 0
        cntErrorsConsecutive = 0
        qry = cls.query(WhysaurusUser.notificationFrequency.IN(['Daily', 'Weekly']))
        for user in qry.iter():        
            # TODO: Renable exception handling once comfortable with reporting
            # try:

            lastSentTime = user.lastEmailSent if user.lastEmailSent else datetime.datetime(2000,1,1)
            now = datetime.datetime.now() 
            today = datetime.datetime(now.year, now.month, now.day)
            lastDaySent = datetime.datetime(lastSentTime.year, lastSentTime.month, lastSentTime.day)            
            timeDelta = today - lastDaySent            
            daysDiff = timeDelta.days
        
            shouldEmail = False

            if user.notificationFrequency == "Daily" and daysDiff >= 1:
                shouldEmail = True
            elif user.notificationFrequency == "Weekly" and daysDiff >= 7:
                shouldEmail = True

            if shouldEmail:
                if not user.canSendUserEmail():
                    logging.info('User %s has unread notifications but email unavailable' % user.name)
                    continue

                logging.info('Checking for active notifications for user %s' % user.name)
                notifications = user.getUnreadNotificationsAfter(lastSentTime)
                if notifications:
                    logging.info('Sending %d notifications to user %s' % (len(notifications), user.name))

                    # generate the email body from the notifications
                    html = handler.template_render(
                        'notificationEmail.html',
                        {'user':user, 'notifications':notifications}
                    )

                    points = [(n.referencePoint.title if n.referencePoint else '') + '\n' for n in notifications]
                    points = list(set(points))
                    text = handler.template_render(
                        'notificationEmailText.html',
                        {'user':user, 'pointTitles':points}
                    )

                    # old version, delete once the new version is working:
                    # mail.send_mail(sender='Whysaurus <community@whysaurus.com>',
                    #    to=[user.email, 'notification.copies@whysaurus.com'],
                    #    subject=user.name + ', People are reacting to your views on Whysaurus!',
                    #    body=text,
                    #    html=html,
                    #    reply_to="community@whysaurus.com"
                    # )
                    
                    # new version:
                    message = mail.EmailMessage(
                        sender='Whysaurus <community@whysaurus.com>',
                        to=user.email,
                        bcc='notification.copies@whysaurus.com',
                        subject=user.name + ' people are reacting to your arguments on Whysaurus!',
                        body=text,
                        reply_to="community@whysaurus.com"
                    )                    
                    if html:
                        message.html = html
                    message.send()
                    # (end of new version)                                    

                    logging.info('Sent mail to user %s' % user.name)
                    # write the time the last notification was sent
                    user.lastEmailSent = datetime.datetime.now()
                    user.put()

            else:
                logging.info('User %s has no unread notifications or was emailed recently' % user.name)

            # except:
            #     logging.error('Exception processing notifications for user: %s' % user.name)
            #     # TODO: Support full error reporting  (Needs google-cloud imports)
            #     # error_reporting.Client().report_exception()
            #     cntErrors += 1
            #     cntErrorsConsecutive += 1
            #     if cntErrorsConsecutive >= 3 or cntErrors >= 10:
            #         logging.error('Too Many Exceptions Processing User Notifications - Abort!')
            #     continue


    def addToSearchIndex(self):
        index = search.Index(name='users')
        fields = [
            search.TextField(name='email', value=self.email),
            search.TextField(name='name', value=self.name),         
        ]
        d = search.Document(doc_id=self.key.urlsafe(), fields=fields)
        index.put(d)

    # delete user does not exist yet; plug this in when it does
    def deleteFromSearchIndex(self):
        doc_index = search.Index(name="users")
        doc_index.delete(self.key.urlsafe())
    
