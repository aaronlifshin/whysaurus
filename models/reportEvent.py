import logging
import datetime
from timezones import PST 
from google.appengine.ext import ndb
from google.appengine.api.taskqueue import Task
from collections import OrderedDict

class DayEventSummary(ndb.Model):
    day = ndb.DateProperty()
    name = ndb.StringProperty()
    count = ndb.IntegerProperty(default=1)
    
    @classmethod
    def getReport(cls):
        q = cls.query()
        q = q.order(-DayEventSummary.day)
        days = {}
        # {'2014-01-27': {u'Login': 7, u'Edit Point': 1, u'Create Point': 1, u'New User': 3}}        
        # Must match the template output order
        defaultDay = OrderedDict((('New User', 0), ('Login', 0), ('Create Point', 0), ('Edit Point' , 0)))
        
        for day in q.iter():            
            if str(day.day) in days:
                days[str(day.day)][day.name] = day.count
            else:
                days[str(day.day)] = defaultDay.copy()
                days[str(day.day)][day.name] = day.count
                

        logging.info(str(days))
        return days
    
class ReportEvent(ndb.Model):
    user = ndb.KeyProperty()
    refEntity1 = ndb.KeyProperty()
    refEntity2 = ndb.KeyProperty()    
    time = ndb.DateTimeProperty()
    count = ndb.IntegerProperty(default=1)
    name = ndb.StringProperty()

    @classmethod
    def recordEvent(cls, userKeyUrlsafe, entityKey1Urlsafe, entityKey2Urlsafe, eventName):
        logging.info('Entered RECORD event')
        userKey = ndb.Key(urlsafe = userKeyUrlsafe)
        entityKey1 = None
        entityKey2 = None
        if entityKey1Urlsafe and entityKey1Urlsafe != '':
            entityKey1 = ndb.Key(urlsafe = entityKey1Urlsafe) 
        if entityKey2Urlsafe and entityKey2Urlsafe != '':
            logging.info('E2US: ++++++ ' + str(entityKey2Urlsafe))
            entityKey2 = ndb.Key(urlsafe = entityKey2Urlsafe)
        
        
        todayPST = PST.convert(datetime.datetime.now())
        dayGMT = datetime.date(todayPST.year, todayPST.month, todayPST.day) 
        
        qry = DayEventSummary.query( 
            DayEventSummary.day == dayGMT, 
            DayEventSummary.name == eventName )
        daySummaries = qry.fetch(1)
        daySummary = None
        if daySummaries:
            daySummary = daySummaries[0]
            
        if daySummary:
            daySummary.count = daySummary.count + 1
        else:
            daySummary = DayEventSummary(
                day=dayGMT, 
                name=eventName)
        
        daySummary.put()
        r = ReportEvent(user=userKey, 
                    refEntity1=entityKey1,
                    refEntity2=entityKey2,
                    time = datetime.datetime.now(),
                    name = eventName)
        r.put()

    @classmethod
    def queueEventRecord(cls, userKeyUrlsafe, entityKey1Urlsafe, entityKey2Urlsafe, eventName):
        taskParams = {
                         'userKeyUrlsafe':userKeyUrlsafe,     
                         'eventName': eventName
                         }
        if entityKey1Urlsafe:
            taskParams['entityKey1Urlsafe'] = entityKey1Urlsafe
        if entityKey2Urlsafe:
            taskParams['entityKey2Urlsafe'] = entityKey2Urlsafe
        
        t = Task(url='/recordEvent', params=taskParams)
        t.add(queue_name="recordEvents")
        
        