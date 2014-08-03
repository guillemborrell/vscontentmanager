from google.appengine.ext import ndb, blobstore

class Subscription(ndb.Model):
    name = ndb.StringProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)


class User(ndb.Model):
    name = ndb.StringProperty()
    password = ndb.StringProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    subscription = ndb.KeyProperty(kind=Subscription)


class Session(ndb.Model):
    when = ndb.DateTimeProperty(auto_now_add = True)
    data = ndb.JsonProperty()


class Page(ndb.Model):
    title = ndb.StringProperty()
    slug = ndb.StringProperty()
    text = ndb.TextProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.UserProperty()
    allowed = ndb.KeyProperty(kind=Subscription)


class Media(ndb.Model):
    name = ndb.StringProperty()
    blob = ndb.BlobKeyProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
