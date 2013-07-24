import json
import logging

from authhandler import AuthHandler
from models.point import Point
from models.source import Source
from models.whysaurusexception import WhysaurusException

def processTreeArrays(titles, levels, dataRefs):
    pointsArray = []
    parentIndex = None
    parentLevel = None
    i = 0
    for title, level, dataRef in zip(titles, levels, dataRefs):
        pd = {'title': title, 'level': int(level), 'dataRef': int(dataRef)}
        if parentIndex is None: # INITIAL SET
            parentIndex = i
            parentLevel = pd['level']
        elif pd['level'] - parentLevel > 1: # WE HAVE A NEW INDENT
            parentIndex = i-1
            parentLevel = parentLevel + 1
        elif pd['level'] <= parentLevel: # UNINDENT 
            for j in range(i-1,-1,-1): # THIS GOES BACK TO 0
                if pointsArray[j]['level'] < pd['level']:                    
                    parentIndex = j
                    parentLevel = pointsArray[j]['level']                      
                    break;               
        if pd['level'] != 0:
            pd['parentIndex'] = parentIndex
        pointsArray = pointsArray + [pd]
        i = i + 1
    return pointsArray

class AddTree(AuthHandler):    
    def post(self):
        jsonOutput = {'result': False}
        user = self.current_user
        titles = json.loads(self.request.get('titles'))
        levels = json.loads(self.request.get('levels'))
        dataRefs = json.loads(self.request.get('dataRefs'))
        pointsData = processTreeArrays(titles, levels, dataRefs)
      
        # sourcesURLs=json.loads(self.request.get('sourcesURLs'))
        # sourcesNames=json.loads(self.request.get('sourcesNames'))
        # rawSources = Source.constructFromArrays(sourcesURLs, sourcesNames)
        
        if user:
            try:
                newMainPoint, newMainPointRoot = Point.createTree(pointsData, user)
            except WhysaurusException as e:
                jsonOutput = {
                    'result': False,
                    'err': str(e)
                }
            else:
                jsonOutput = {
                    'result': True,
                    'url': newMainPoint.url,
                    'rootKey': newMainPointRoot.key.urlsafe()
                }
            resultJSON = json.dumps(jsonOutput)
            logging.info('Tree %s' % resultJSON)
        else:
            resultJSON = json.dumps({'result': False, 'error': 'You appear not to be logged in.'})
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
