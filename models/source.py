from google.appengine.ext import ndb

class Source(ndb.Model):
    url = ndb.StringProperty()
    name = ndb.StringProperty()

    @staticmethod
    def constructFromArrays(urls, titles, parentPointKey):
        sources = []
        for url, title in zip(urls, titles):
            newSource = Source(parent=parentPointKey)
            newSource.url = url
            newSource.name = title
            sources = sources + [newSource]
        return sources

