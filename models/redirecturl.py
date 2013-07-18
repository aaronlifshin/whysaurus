from google.appengine.ext import ndb

class RedirectURL(ndb.Model):
    fromURL = ndb.StringProperty()
    toURL = ndb.StringProperty()
    numCopies = ndb.IntegerProperty(default=0)

    @staticmethod
    def getByFromURL(url):
        redirectQuery = RedirectURL.gql("WHERE fromURL= :1", url)
        redirectURL = redirectQuery.get()
        if redirectURL:
            return redirectURL.toURL
        else:
            return None

    @staticmethod
    def updateRedirects(toURL, updatedToURL):
        redirectQuery = RedirectURL.gql("WHERE toURL= :1", toURL)
        redirectURLs = redirectQuery.fetch(50)
        for redirectURL in redirectURLs:
            redirectURL.toURL = updatedToURL
            redirectURL.put()
