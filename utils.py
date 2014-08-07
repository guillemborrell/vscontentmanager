from google.appengine.api import users


AUTHORIZED_USERS = ['guillemborrell@gmail.com',
                    'beatriz88rc@gmail.com',
                    'c.protocolservices@gmail.com']

def check_user(user):
    if user:
        if user.email() in AUTHORIZED_USERS:
            return user, users.create_logout_url('/')

        else:
            return False, False

    else:
        return False, False
