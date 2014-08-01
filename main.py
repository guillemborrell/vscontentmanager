import os
import webapp2
import jinja2
from google.appengine.api import users
from models import User, Session, Page, Subscription

AUTHORIZED_USERS = ['guillemborrell@gmail.com']

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
                self.response.write(template.render({'auth': True,
                                                 'page': page}))
            
            else:
                template = JINJA_ENVIRONMENT.get_template('404.html')
                self.response.write(template.render({}))
                

        else:
            self.redirect('/login?to={}'.format(slug))


class AdminPage(webapp2.RequestHandler):
    def get(self,slug):
        user, logout = check_user(users.get_current_user())
        if user:
            page = Page.query(Page.slug == slug).fetch(1)
            if page:
                page = page[0]
                template = JINJA_ENVIRONMENT.get_template('admin.html')
                self.response.write(template.render(
                    {'auth':True,
                     'page':page,
                     'logout_url':users.create_logout_url('/')}))
            else:
                template = JINJA_ENVIRONMENT.get_template('404.html')
                self.response.write(template.render({}))
                
        else:
            template = JINJA_ENVIRONMENT.get_template('admin.html')
            self.response.write(template.render(
                {'auth':False,
                 'login_url': users.create_login_url('/admin')}))



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
        webapp2.Route(r'/admin/<slug:.*>',AdminPage),
        webapp2.Route(r'/boot',BootPage)
    ], debug = True)
