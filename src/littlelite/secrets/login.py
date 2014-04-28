""" 
 SECRETS 
 A LittleLite Web Application
 
 login.py

"""

import logging
import littlelite.db.queries

# Google Imports
from google.appengine.api import users

class Login(object):
    """ Login class """
    
    def __init__(self):
        self.__user = users.get_current_user()
        self.__is_logged = False
        self.__is_registered = False
        self.__username = 'Unknown'
        if (self.__user):
            self.__is_logged = True
            self.__email = self.__user.email()
            self.__is_registered = self.__is__user_on_db()
            self.__set_name()
                    
    #Public members
    def is_first_time(self):
        ''' If user is first time on the system '''
        if ((self.__is_logged) and (not self.__is_registered)):
            return True
        return False
    
    def is_registered(self):
        ''' If user is registered '''
        if (self.__is_registered):
            return True
        return False
    
    def is_admin(self):
        ''' If user is admin '''
        return users.is_current_user_admin()
    
    def quota(self):
        """ User's quota """
        return self.__db_user().quota
    
    #Private members
    def __set_name(self):
        name = self.__user.nickname()
        idx = name.find('@')
        if (idx > 0):
            name = name[:idx]
        self.__username = name
        
    def __is_user_logged(self): #IGNORE:C0111
        return self.__is_logged

    def __user_name(self): #IGNORE:C0111
        return self.__username
    
    def __google_user(self):  #IGNORE:C0111
        return self.__user
    
    def __user_email(self): #IGNORE:C0111
        return self.__email
    
    def __db_user(self): #IGNORE:C0111
        return littlelite.db.queries.UserQueries.get_dbuser(self.__user)

    def __is__user_on_db(self): #IGNORE:C0111
        result = self.__db_user()
        if (result):
            self.__username = result.username
            logging.debug('Found user '+ self.__username +' on DB')
            return True
        return False
        
    def __str__(self):
        loginstr = ''
        if (self.__is_logged):
            loginstr = 'Logged as %s' % self.__username
            if (users.is_current_user_admin()):
                loginstr += "(admin)"
            if (self.__is_registered):
                loginstr += "(registered)"
        else:
            loginstr = 'Not logged in (unknown)'
        return loginstr
    
    #Login properties
    is_logged = property(fget=__is_user_logged, doc="If current user is logged in")
    username = property(fget=__user_name, doc="Current user's name")
    google_user = property(fget=__google_user, doc="Current Google user object")
    user = property(fget=__db_user, doc="Current user DB object (SecretsUser)")
    email = property(fget=__user_email, doc="Current user's e-mail")
    
    
