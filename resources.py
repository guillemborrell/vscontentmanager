import json
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from models import User, Session, Page, Subscription
from models import Media, Message, Task, Group


class UserResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            if self.request.get('id'):
                u = [ndb.Key(urlsafe=self.request.get('id')).get()]
                data = json.dumps([u.to_dict()])
                
            elif self.request.get('page'):
                if self.request.get('page') == 'start':
                    curs = None
                else:
                    curs = Cursor(urlsafe=self.request.get('page'))
                    
                u = []
                more = True

                while more:
                    d, curs, more = User.query().order(-User.when).fetch_page(10, start_cursor=cursor)
                    for ditem in d:
                        u.apppend(ditem)
                        
            else:
            data = []
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(data)



    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            User(name = body['name'],
                 password = body['password'],
                 subscription = body['subscription'],
                 group = ndb.Key(urlsafe=body['group'])).put()


    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            task = ndb.Key(urlsafe=key)
            task.delete()



class SubscriptionResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            if self.request.get('id'):
                u = [ndb.Key(urlsafe=self.request.get('id')).get()]
                data = json.dumps([u.to_dict()])
                
            elif self.request.get('page'):
                if self.request.get('page') == 'start':
                    curs = None
                else:
                    curs = Cursor(urlsafe=self.request.get('page'))
                    
                u = []
                more = True

                while more:
                    d, curs, more = Subscription.query().order(-Subscription.when).fetch_page(10, start_cursor=cursor)
                    for ditem in d:
                        u.apppend(ditem)
                        
            else:
            data = []
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(data)



    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            Subscription(name = body['name'],
                         level = body['level']).put()


    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            task = ndb.Key(urlsafe=key)
            task.delete()
            

class GroupResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            if self.request.get('id'):
                u = [ndb.Key(urlsafe=self.request.get('id')).get()]
                data = json.dumps([u.to_dict()])
                
            elif self.request.get('page'):
                if self.request.get('page') == 'start':
                    curs = None
                else:
                    curs = Cursor(urlsafe=self.request.get('page'))
                    
                u = []
                more = True

                while more:
                    d, curs, more = Group.query().order(-Group.when).fetch_page(10, start_cursor=cursor)
                    for ditem in d:
                        u.apppend(ditem)
                        
            else:
            data = []
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(data)



    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            Group(name = body['name']).put()


    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            task = ndb.Key(urlsafe=key)
            task.delete()


class TaskResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            if self.request.get('id'):
                u = [ndb.Key(urlsafe=self.request.get('id')).get()]
                data = json.dumps([u.to_dict()])
                
            elif self.request.get('page'):
                if self.request.get('page') == 'start':
                    curs = None
                else:
                    curs = Cursor(urlsafe=self.request.get('page'))
                    
                u = []
                more = True

                while more:
                    d, curs, more = Task.query().order(-Task.when).fetch_page(10, start_cursor=cursor)
                    for ditem in d:
                        u.apppend(ditem)
                        
            else:
            data = []
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(data)



    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            Task(name = body['name'],
                 kind = body['kind'],
                 data = body['data']).put()


    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            task = ndb.Key(urlsafe=key)
            task.delete()


class AssignmentResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            if self.request.get('id'):
                u = [ndb.Key(urlsafe=self.request.get('id')).get()]
                data = json.dumps([u.to_dict()])
                
            elif self.request.get('page'):
                if self.request.get('page') == 'start':
                    curs = None
                else:
                    curs = Cursor(urlsafe=self.request.get('page'))
                    
                u = []
                more = True

                while more:
                    d, curs, more = Assignment.query().order(-Assignment.when).fetch_page(10, start_cursor=cursor)
                    for ditem in d:
                        u.apppend(ditem)
                        
            else:
            data = []
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(data)



    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            Task(name = body['name'],
                 kind = body['kind'],
                 data = body['data']).put()


    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            task = ndb.Key(urlsafe=key)
            task.delete()

