from google.appengine.ext import ndb, blobstore

class Subscription(ndb.Model):
    name = ndb.StringProperty()
    level = ndb.IntegerProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)


class User(ndb.Model):
    name = ndb.StringProperty()
    password = ndb.StringProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    subscription = ndb.IntegerProperty()


class Session(ndb.Model):
    when = ndb.DateTimeProperty(auto_now_add = True)
    data = ndb.JsonProperty()


class Page(ndb.Model):
    title = ndb.StringProperty()
    slug = ndb.StringProperty()
    text = ndb.TextProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.UserProperty()
    allowed = ndb.IntegerProperty()


class Media(ndb.Model):
    name = ndb.StringProperty()
    blob = ndb.BlobKeyProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)


class Message(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    message = ndb.TextProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
