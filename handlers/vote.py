import json
import logging
from authhandler import AuthHandler
from models.point import Point


class Vote(AuthHandler):
    def post(self):
        resultJSON = json.dumps({'result': False})
        point, pointRoot = Point.getCurrentByUrl(self.request.get('pointURL'))
        user = self.current_user
        if point and user:
            if user.addVote(point, int(self.request.get('vote'))):
                resultJSON = json.dumps({'result': True, 'newVote': self.request.get('vote')})
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)

    def relevanceVote(self):
        resultJSON = json.dumps({'result': False})
        parentRootURLsafe = self.request.get('parentRootURLsafe')
        childRootURLsafe = self.request.get('childRootURLsafe')
        linkType = self.request.get('linkType')
        vote = self.request.get('vote')        
        user = self.current_user
        
        if int(vote) > 100 or int(vote) < 0:
            resultJSON = json.dumps({'result': False, 'error':'Vote value out of range.'})
            
        # logging.info('ABOUT TO CHECK ALL THE DATA 1:%s 2:%s 3:%s 4:%s ' % (parentRootURLsafe,childRootURLsafe,linkType, vote))
        elif parentRootURLsafe and childRootURLsafe and linkType and user:
            result, newRelevance, newVoteCount = user.addRelevanceVote(
                parentRootURLsafe, childRootURLsafe, linkType, int(vote))
            if result:
                resultJSON = json.dumps({
                    'result': True, 
                    'newVote': vote,
                    'newRelevance': str(newRelevance) + ' %',
                    'newVoteCount': newVoteCount
                })
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)       

