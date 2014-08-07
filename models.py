from google.appengine.ext import ndb, blobstore

class Subscription(ndb.Model):
    name = ndb.StringProperty()
    level = ndb.IntegerProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)

    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "name": self.name,
                "level": self.level,
                "when": self.when.strftime("%b %d %Y %H:%M:%S")}

class Group(ndb.Model):
    name = ndb.StringProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    active = ndb.BooleanProperty()
    
    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "name": self.name,
                "active": self.active,
                "when": self.when.strftime("%b %d %Y %H:%M:%S")}


class User(ndb.Model):
    name = ndb.StringProperty()
    password = ndb.StringProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    subscription = ndb.KeyProperty(kind=Subscription)
    group = ndb.KeyProperty(kind=Group)

    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "name": self.name,
                "password": self.password,
                "when": self.when.strftime("%b %d %Y %H:%M:%S"),
                "subscription": self.subscription.get().name,
                "group": self.group.get().name}


class Session(ndb.Model):
    when = ndb.DateTimeProperty(auto_now_add = True)
    data = ndb.JsonProperty()

    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "when": self.when.strftime("%b %d %Y %H:%M:%S"),
                "data": self.data}


class Page(ndb.Model):
    title = ndb.StringProperty()
    slug = ndb.StringProperty()
    text = ndb.TextProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.UserProperty()
    allowed = ndb.IntegerProperty()

    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "title": self.title,
                "slug": self.slug,
                "text": self.text,
                "when": self.when.strftime("%b %d %Y %H:%M:%S"),
                "author": self.author.nickname(),
                "allowed": self.allowed}


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

    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "name": self.name,
                "email": self.email,
                "phone": self.phone,
                "message": self.message,
                "when": self.when.strftime("%b %d %Y %H:%M:%S")}


class Task(ndb.Model):
    name = ndb.StringProperty()
    kind = ndb.StringProperty()
    data = ndb.JsonProperty()
    when = ndb.DateTimeProperty(auto_now_add = True)
    active = ndb.BooleanProperty

    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "name": self.name,
                "kind": self.kind,
                "data": self.data,
                "active": self.active,
                "when": self.when.strftime("%b %d %Y %H:%M:%S")}


class Assignment(ndb.Model):
    when = ndb.DateTimeProperty(auto_now_add = True)
    task = ndb.KeyProperty()
    user = ndb.KeyProperty()
    duration_in_minutes = ndb.IntegerProperty()
    start = ndb.DateTimeProperty()
    due = ndb.DateTimeProperty()
    result = ndb.JsonProperty()
    completed = ndb.BooleanProperty()
    revised = ndb.BooleanProperty()

    def to_dict(self):
        return {"id": self.key.urlsafe(),
                "when": self.when.strftime("%b %d %Y %H:%M:%S"),
                "task": self.task.urlsafe(),
                "user": self.user.urlsafe(),
                "duration_in_minutes": self.duration_in_minutes,
                "start": self.start.strftime("%b %d %Y %H:%M:%S"),
                "due": self.due.strftime("%b %d %Y %H:%M:%S"),
                "completed": self.completed,
                "revised": self.revised}
