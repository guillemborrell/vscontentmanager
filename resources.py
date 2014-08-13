import json
import webapp2
import datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from models import User, Session, Page, Subscription
from models import Media, Message, Task, Group, Assignment

from utils import check_user, AUTHORIZED_USERS

class UserResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            u = []
            more = True
            cursor = None

            while more:
                d, cursor, more = User.query().order(
                    -User.when).fetch_page(10, start_cursor=cursor)
                for ditem in d:
                    u.append(ditem.to_dict())
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'data':u}))


    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            User(name = body['name'],
                 password = body['password'],
                 subscription = ndb.Key(urlsafe=body['subscription']),
                 group = ndb.Key(urlsafe=body['group'])).put()


    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            u = ndb.Key(urlsafe=key)
            u.delete()



class SubscriptionResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            u = []
            more = True
            cursor = None
            while more:
                d, cursor, more = Subscription.query().order(-Subscription.when).fetch_page(10, start_cursor=cursor)
                for ditem in d:
                    u.append(ditem.to_dict())

                                    
        self.response.out.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'data':u}))


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
            u = []
            more = True
            cursor = None
            while more:
                d, curs, more = Group.query(
                    Group.active == True).order(
                        -Group.when).fetch_page(
                            10, start_cursor=cursor)
                for ditem in d:
                    u.append(ditem.to_dict())
                        
        else:
            u = []
            
        self.response.out.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'data':u}))



    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            Group(name = body['name'],
                  active = True).put()


    @ndb.transactional
    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            g = ndb.Key(urlsafe=key).get()
            g.active = False
            g.put()


class TaskResource(webapp2.RequestHandler):
    def get(self):
        if self.request.get('id'):
            u = ndb.Key(urlsafe=self.request.get('id')).get().to_dict()
            
        else:
            cursor = None
            u = []
            more = True
            
            while more:
                d, cursor, more = Task.query(
                    Task.active == True).order(
                        -Task.when).fetch_page(
                            10, start_cursor=cursor)
                for ditem in d:
                    u.append(ditem.to_dict())
                    
        self.response.out.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({'data':u}))


    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)
            if self.request.get('id'):
                task = ndb.Key(urlsafe=self.request.get('id')).get()
                task.data = body['data']
                task.put()
            else:
                Task(name = body['name'],
                     kind = body['kind'],
                     active = True,
                     data = body['data']).put()
                
            
    @ndb.transactional
    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            task = ndb.Key(urlsafe=key).get()
            task.active = False
            task.put()


class AssignmentResource(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            if self.request.get('id'):
                t = ndb.Key(urlsafe=self.request.get('id')).get()
                u = t.to_dict()
                t.revised = True
                t.put()
                
            else:
                cursor = None
                u = []
                more = True

                while more:
                    d, curs, more = Assignment.query(
                        Assignment.active == True).order(
                            -Assignment.when).fetch_page(
                                100, start_cursor=cursor)
                    for ditem in d:
                        u.append(ditem.to_dict())
                        
            
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({'data':u}))


    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            body = json.loads(self.request.body)

            assigned_users = User.query(
                User.group == ndb.Key(urlsafe=body['group'])).fetch(100)

            for u in assigned_users:
                Assignment(
                    task = ndb.Key(urlsafe=body['task']),
                    user = u.key,
                    duration_in_minutes = int(body['duration_in_minutes']),
                    start = datetime.datetime.strptime(
                        body['start'],
                        "%a, %d %b %Y %H:%M:%S %Z"),
                    due = datetime.datetime.strptime(
                        body['due'],
                        "%a, %d %b %Y %H:%M:%S %Z"),
                    result = {},
                    completed = False,
                    revised = False,
                    active = True,
                ).put()
            

    @ndb.transactional
    def delete(self):
        user, logout = check_user(users.get_current_user())
        if user:
            key = self.request.get('id')
            #even more things here
            assignment = ndb.Key(urlsafe=key).get()
            assignment.active = False
            assignment.put()


class MakeAssignmentResource(webapp2.RequestHandler):
    def get(self):
        assignment = ndb.Key(urlsafe=self.request.get('id')).get()
        self.response.out.headers['Content-Type'] = 'application/json'
        self.response.out.write(
            json.dumps({'data':assignment.to_dict()})
        )
        assignment.completed = True
        assignment.when = datetime.datetime.now()
        assignment.put()

    @ndb.transactional
    def post(self):
        key = self.request.get('id')
        assignment = ndb.Key(urlsafe=key).get()
        body = json.loads(self.request.body)
        assignment.result = body['data']
        assignment.put()
        
