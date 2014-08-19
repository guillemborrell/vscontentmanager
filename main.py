import os
import webapp2
import jinja2
import re
import urllib
import json
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from models import User, Session, Page, Subscription
from models import Media, Message, Task, Group, Assignment
from resources import UserResource, GroupResource, TaskResource
from resources import AssignmentResource, SubscriptionResource
from resources import MakeAssignmentResource
from utils import check_user, AUTHORIZED_USERS


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'static')
    ),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



def process_text(text):
    # Process the small markup here.
    slugs = re.findall(r"#(\w+)",text)
    replacements = list()
    for slug in slugs:
        page = Page.query(Page.slug == slug).fetch(1)
        if page:
            replacements.append('app')
            replacements.append('<i class="fa fa-external-link-square"></i>')
        else:
            replacements.append('content')
            replacements.append('')

    newtext = re.sub(r"#(\w+)", '<a href="/{}/\g<1>">{}</a>', text)
    return newtext.format(*replacements)


def process_text_admin(text):
    # Process the small markup here.
    slugs = re.findall(r"#(\w+)",text)
    replacements = list()
    for slug in slugs:
        page = Page.query(Page.slug == slug).fetch(1)
        if page:
            replacements.append('content')
            replacements.append('<i class="fa fa-external-link-square"></i>')
        else:
            replacements.append('content')
            replacements.append('<i class="fa fa-edit"></i>')

    newtext = re.sub(r"#(\w+)", '<a href="/{}/\g<1>">{}</a>', text)
    return newtext.format(*replacements)


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

    def post(self):
        Message(name = self.request.get('name'),
                email = self.request.get('email'),
                phone = self.request.get('phone'),
                message = self.request.get('message')).put()


class AppPage(webapp2.RequestHandler):
    def get(self,slug):
        cookie = self.request.cookies.get('CookieProtocolServices')
        if cookie:
            session = ndb.Key(urlsafe=str(cookie)).get()
            user = session.key.parent().get()
            page = Page.query(Page.slug == slug).get()
            assignments = Assignment.query(
                Assignment.user == user.key,
                Assignment.completed == False).order(
                    -Assignment.when).fetch(10)

            if page:
                #TODO: Manage subscriptions
                template = JINJA_ENVIRONMENT.get_template('app.html')
                self.response.write(template.render(
                    {'auth': True,
                     'page': page,
                     'user': user,
                     'assignments': assignments,
                     'text': process_text(page.text)}))
            
            else:
                template = JINJA_ENVIRONMENT.get_template('404.html')
                self.response.write(template.render({}))
                

        else:
            self.redirect('/login?to={}'.format(slug))


class AdminPage(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            message_list = list()
            more = True
            curs = None
            while more:
                m, curs, more = Message.query(
                ).order(
                    -Message.when).fetch_page(
                        10, start_cursor=curs)
                for mitem in m:
                    message_list.append(mitem)


            template = JINJA_ENVIRONMENT.get_template('admin.html')
            self.response.write(template.render(
                {'logout_url':users.create_logout_url('/'),
                 'messages': message_list}))

        else:
            self.redirect(users.create_login_url('/admin'))


class ContentPage(webapp2.RequestHandler):
    def get(self,slug):
        user, logout = check_user(users.get_current_user())
        if user:
            page = Page.query(Page.slug == slug).fetch(1)
            template_args = {'logout_url': users.create_logout_url('/')}
            if page:
                page = page[0]
                template_args['new'] = False
                template_args['title'] = page.title
                template_args['text'] = process_text_admin(page.text)
                template_args['edit'] = page.text
                template_args['subscription'] = Subscription.query(
                    Subscription.level == page.allowed).get().name
                template_args['subscriptions'] = Subscription.query().fetch(10)
                template_args['slug'] = page.slug
                template_args['author'] = user.nickname()
            
            else:
                template_args['new'] = True
                template_args['title'] = ''
                template_args['text'] = ''
                template_args['edit'] = ''
                template_args['subscriptions'] = Subscription.query().fetch(10)
                template_args['slug'] = slug
                template_args['author'] = user.nickname()
        
            template = JINJA_ENVIRONMENT.get_template('content.html')
            self.response.write(template.render(template_args))

        
        else:
            self.redirect('/admin')

    def post(self,slug):
        page = Page.query(Page.slug == slug).fetch(1)
        if page:
            subscription = Subscription.query(
                Subscription.name == self.request.get('subscription')
            ).get()
            page = page[0].key.get()
            page.slug = slug
            page.title = self.request.get('title')
            page.text = self.request.get('text')
            page.allowed = subscription.level
            page.put()

            self.redirect('/content/{}'.format(slug))
        
        else:
            subscription = Subscription.query(
                Subscription.name == self.request.get('subscription')
            ).get()
            page = Page(title = self.request.get('title'),
                        slug = slug,
                        author = users.get_current_user(),
                        text = self.request.get('text'),
                        allowed = subscription.level)
            page.put()
        
            self.redirect('/content/{}'.format(slug))


class MediaPage(webapp2.RequestHandler):
    ## This object is non REST rubbish, but I don't care.
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            upload_url = blobstore.create_upload_url('/upload')
            template_args = {'logout_url': users.create_logout_url('/')}
            media_list = list()
            more = True
            curs = None
            while more:
                m, curs, more = Media.query(
                ).order(
                    -Media.when).fetch_page(
                        10, start_cursor=curs)
                for mitem in m:
                    media_list.append(mitem)

            template_args['media'] = media_list
            template_args['upload_url'] = upload_url

            template = JINJA_ENVIRONMENT.get_template('media.html')
            self.response.write(template.render(template_args))

        else:
            self.redirect('/admin')


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            upload_files = self.get_uploads('file')
            for i,f in enumerate(upload_files):
                blob_info = f
                Media(name = self.request.get('name')+'_{}'.format(i),
                      blob = blob_info.key()).put()
            
            self.redirect('/media')
            
        else:
            self.redirect('/media')
            

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class UserPage(webapp2.RequestHandler):
    def get(self):
        cookie = self.request.cookies.get('CookieProtocolServices')
        admin, logout = check_user(users.get_current_user())

        if cookie:
            session = ndb.Key(urlsafe=str(cookie)).get()
            user = session.key.parent().get()

            assignments = Assignment.query(
                Assignment.active == True,
                Assignment.user == user.key,
                Assignment.completed == False).order(
                    -Assignment.when).fetch(10)


            template = JINJA_ENVIRONMENT.get_template('user.html')
            self.response.write(template.render(
                {'auth': False,
                 'user': user.to_dict(),
                 'assignments': assignments}))


        elif admin:
            user = ndb.Key(urlsafe=self.request.get('id')).get()

            assignments = Assignment.query(
                Assignment.user == user.key,
                Assignment.completed == False).order(
                    -Assignment.when).fetch(10)


            template = JINJA_ENVIRONMENT.get_template('user.html')
            self.response.write(template.render(
                {'auth': True,
                 'user': user.to_dict(),
                 'assignments': assignments}))
            

        else:
            self.redirect('/login?to={}'.format(slug))


class LoginPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(
            template.render({'to':self.request.get('to')})
        )

    def post(self):
        username = self.request.get('user')
        password = self.request.get('password')
        to = self.request.get('to')

        user = User.query(User.name == username,
                          User.password == password).get()

        if user:
            session = Session(parent = user.key,
                              data = {})
            template = JINJA_ENVIRONMENT.get_template('app.html')
            session.put()

            self.response.set_cookie(
                'CookieProtocolServices',
                session.key.urlsafe(),
                max_age=32000)

            self.redirect('/app/{}'.format(to))
            

        else:
            self.redirect('/login')


class LogoutPage(webapp2.RequestHandler):
    def get(self):
        self.response.delete_cookie('CookieProtocolServices')
        self.redirect('/')


class BlogPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('blog.html')
        if self.request.get('id'):
            pages = Page.query(Page.allowed == 0,
                               Page.slug == self.request.get('id')).fetch(1)
        else:
            pages = Page.query(Page.allowed == 0).order(-Page.when).fetch(10)
            
        self.response.write(
            template.render({'pages':pages})
        )


class BootPage(webapp2.RequestHandler):
    def get(self):
        public = Subscription(name='public',
                              level=0)
        public.put()

        subscription = Subscription(name='standard',
                                    level=1)
        subscription.put()

        User(name='test',
             password='test',
             subscription=subscription.level).put()
 
        Page(title='Home',
             slug ='home',
             text ='Lorem ipsum...',
             allowed = subscription.level,
             author = users.User('none@none.com')).put()

        self.redirect('/')


## HERE IS WHERE THE REST STARTS
class ActivityPage(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            template_args = {'logout_url': users.create_logout_url('/')}

            task_list = list()
            more = True
            curs = None
            while more:
                t, curs, more = Task.query(
                ).fetch_page(
                    10, start_cursor=curs)
                for titem in t:
                    task_list.append(titem)

            template_args['tasks'] = task_list

            template = JINJA_ENVIRONMENT.get_template('activity.html')
            self.response.write(template.render(template_args))

        else:
            self.redirect('/admin')


class UsersPage(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            template_args = {'logout_url': users.create_logout_url('/')}
            subscription_list = list()
            more = True
            curs = None
            while more:
                s, curs, more = Subscription.query(
                ).fetch_page(
                    10, start_cursor=curs)
                for sitem in s:
                    subscription_list.append(sitem)

            template_args['subscriptions'] = subscription_list

            users_list = list()
            more = True
            curs = None
            while more:
                u, curs, more = User.query(
                ).order(
                    -User.when).fetch_page(
                        10, start_cursor=curs)
                for uitem in u:
                    users_list.append(uitem)

            template_args['users'] = users_list

            template = JINJA_ENVIRONMENT.get_template('users.html')
            self.response.write(template.render(template_args))

        else:
            self.redirect('/admin')


class TaskPage(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            template_args = {
                'logout_url': users.create_logout_url('/')
            }
            
            template = JINJA_ENVIRONMENT.get_template('task.html')
            self.response.write(
                template.render(template_args)
            )

        else:
            self.redirect('/admin')


class ViewTaskPage(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            template_args = {
                'logout_url': users.create_logout_url('/')
            }
            
            template = JINJA_ENVIRONMENT.get_template('viewtask.html')
            self.response.write(
                template.render(template_args)
            )

        else:
            self.redirect('/admin')



class AssignPage(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            template_args = {
                'logout_url': users.create_logout_url('/')
            }
            
            template = JINJA_ENVIRONMENT.get_template('assign.html')
            self.response.write(
                template.render(template_args)
            )

        else:
            self.redirect('/admin')


class MakeAssignmentPage(webapp2.RequestHandler):
    def get(self):
        cookie = self.request.cookies.get('CookieProtocolServices')
        if cookie:
            session = ndb.Key(urlsafe=str(cookie)).get()
            user = session.key.parent().get()

            template_args = {'user': user}
            
            template = JINJA_ENVIRONMENT.get_template('makeassignment.html')
            self.response.write(
                template.render(template_args)
            )

        else:
            self.redirect('/login?to={}'.format(slug))


class ReviewAssignmentPage(webapp2.RequestHandler):
    def get(self):
        user, logout = check_user(users.get_current_user())
        if user:
            template_args = {
                'logout_url': users.create_logout_url('/')
            }

            template = JINJA_ENVIRONMENT.get_template('reviewassignment.html')
            self.response.write(
                template.render(template_args)
            )

        else:
            self.redirect('/login?to={}'.format(slug))



app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/',MainPage),
        webapp2.Route(r'/app/<slug:.*>',AppPage),
        webapp2.Route(r'/user',UserPage),
        webapp2.Route(r'/login',LoginPage),
        webapp2.Route(r'/logout',LogoutPage),
        webapp2.Route(r'/admin',AdminPage),
        webapp2.Route(r'/content/<slug:.*>',ContentPage),
        webapp2.Route(r'/media',MediaPage),
        webapp2.Route(r'/upload',UploadHandler),
        webapp2.Route(r'/serve/<resource:.*>',ServeHandler),
        webapp2.Route(r'/users',UsersPage),
        webapp2.Route(r'/activity',ActivityPage),
        webapp2.Route(r'/assign',AssignPage),
        webapp2.Route(r'/blog',BlogPage),
        webapp2.Route(r'/boot',BootPage),
        webapp2.Route(r'/task',TaskPage),
        webapp2.Route(r'/viewtask',ViewTaskPage),
        webapp2.Route(r'/makeassignment',MakeAssignmentPage),
        webapp2.Route(r'/reviewassignment',ReviewAssignmentPage),
        webapp2.Route(r'/REST/user',UserResource),
        webapp2.Route(r'/REST/group',GroupResource),
        webapp2.Route(r'/REST/subscription',SubscriptionResource),
        webapp2.Route(r'/REST/task',TaskResource),
        webapp2.Route(r'/REST/assignment',AssignmentResource),
        webapp2.Route(r'/REST/makeassignment',MakeAssignmentResource)
    ], debug = True)
