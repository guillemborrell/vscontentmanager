import os
import webapp2
import jinja2
import re
from google.appengine.api import users
from google.appengine.ext import ndb
from models import User, Session, Page, Subscription

AUTHORIZED_USERS = ['guillemborrell@gmail.com',
                    'beatriz88rc@gmail.com']

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'static')
    ),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def check_user(user):
    if user:
        if user.email() in AUTHORIZED_USERS:
            return user, users.create_logout_url('/')

        else:
            return False, False

    else:
        return False, False

def process_text(text):
    # Process the small markup here.
    slugs = re.findall(r"#(\w+)",text)
    replacements = list()
    for slug in slugs:
        page = Page.query(Page.slug == slug).fetch(1)
        if page:
            replacements.append('app')
            replacements.append('<i class="fa fa-external-link"></i>')
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
            replacements.append('<i class="fa fa-external-link"></i>')
        else:
            replacements.append('content')
            replacements.append('<i class="fa fa-edit"></i>')

    newtext = re.sub(r"#(\w+)", '<a href="/{}/\g<1>">{}</a>', text)
    return newtext.format(*replacements)


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))


class AppPage(webapp2.RequestHandler):
    def get(self,slug):
        cookie = self.request.cookies.get('CookieProtocolServices')
        if cookie:
            page = Page.query(Page.slug == slug).fetch(1)
            if page:
                #TODO: Manage subscriptions
                page = page[0]
                template = JINJA_ENVIRONMENT.get_template('app.html')
                self.response.write(template.render(
                    {'auth': True,
                     'page': page,
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
            template = JINJA_ENVIRONMENT.get_template('admin.html')
            self.response.write(template.render(
                {'logout_url':users.create_logout_url('/')}))

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
                template_args['subscription'] = page.allowed.get().name
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
            ).fetch(1)
            page = page[0].key.get()
            page.slug = slug
            page.title = self.request.get('title')
            page.text = self.request.get('text')
            page.allowed = subscription[0].key
            page.put()

            self.redirect('/content/{}'.format(slug))
        
        else:
            subscription = Subscription.query(
                Subscription.name == self.request.get('subscription')
            ).fetch(1)
            page = Page(title = self.request.get('title'),
                        slug = slug,
                        text = self.request.get('text'),
                        allowed = subscription[0].key)
            page.put()
        
            self.redirect('/content/{}'.format(slug))


class MediaPage(webapp2.RequestHandler):
    def get(self,slug):
        pass


class UsersPage(webapp2.RequestHandler):
    ## This object is non REST rubbish, but I don't care.
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

    def post(self):
        user, logout = check_user(users.get_current_user())
        if user:
            what = self.request.get('what')
            action = self.request.get('action')

            if what == 'subscription' and action == 'create':
                Subscription(name=self.request.get('name')).put()
                
            elif what == 'user' and action == 'delete':
                user = ndb.Key(urlsafe=self.request.get('key'))
                user.delete()

            elif what == 'user' and action == 'create':
                User(
                    name = self.request.get('name'),
                    password = self.request.get('password'),
                    subscription = Subscription.query(
                        Subscription.name == self.request.get(
                            'subscription')
                    ).fetch(1)[0].key).put()


        self.redirect('/users')


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

        result = User.query(User.name == username,
                            User.password == password).fetch(1)

        if result:
            user = result[0]
            session = Session(parent = user.key,
                              data = {})
            template = JINJA_ENVIRONMENT.get_template('app.html')
            self.response.set_cookie(
                'CookieProtocolServices',
                session.key.urlsafe(),
                max_age=32000)
                 
            session.put()                    
            self.redirect('/app/{}'.format(to))
            

        else:
            self.redirect('/login')


class LogoutPage(webapp2.RequestHandler):
    def get(self):
        self.response.delete_cookie('CookieProtocolServices')
        self.redirect('/')


class BootPage(webapp2.RequestHandler):
    def get(self):
        subscription = Subscription(name='standard')
        subscription.put()

        User(name='test',
             password='test',
             subscription=subscription.key).put()
 
        Page(title='Home',
             slug ='home',
             text ='Lorem ipsum...',
             allowed = subscription.key,
             author = users.User('none@none.com')).put()

        self.redirect('/')

app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/',MainPage),
        webapp2.Route(r'/app/<slug:.*>',AppPage),
        webapp2.Route(r'/login',LoginPage),
        webapp2.Route(r'/logout',LogoutPage),
        webapp2.Route(r'/admin',AdminPage),
        webapp2.Route(r'/content/<slug:.*>',ContentPage),
        webapp2.Route(r'/media',MediaPage),
        webapp2.Route(r'/users',UsersPage),
        webapp2.Route(r'/boot',BootPage)
    ], debug = True)
