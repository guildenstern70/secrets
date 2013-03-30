""" 
 SECRETS 
 A LittleLite Web Application
 
 utils.py

"""

import logging

# Google Imports
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import mail

class Folders(object):
    """ Folders enumeration """
    INBOX = 'inbox'
    SENT = 'sent'
    ARCHIVE = 'archive'
    DRAFT = 'draft'
    TRASH = 'trash'

class MailAddr(object):
    """ Mail object wrapper """
    
    def __init__(self, email):
        self.email_complete = email
        self.email_address = self.__address_from_email()
        
    def __str__(self):
        return self.email_address
    
    def __get_complete(self):
        return self.email_complete
    
    def __address_from_email(self):
        """ Extract email address from complete email, ie: Alessio <alessio@altes.it> """
        address = self.email_complete
        idx_start = address.find('<')
        if (idx_start > 0):
            idx_end = address.rfind('>')
            address = address[idx_start+1:idx_end]
            logging.debug('E-mail address for '+ self.email_complete+' is: '+ address)
        return address

    #Properties
    address = property(fget=__str__, doc="The e-mail address in the e-mail")
    complete = property(fget=__get_complete, doc="The complete email, ie: Alessio <alessio@altes.it>")
    
    
class Mailer(object):
    """ Mail related class """
    
    def __init__(self):
        if (users.get_current_user()):
            self.sender_email = users.get_current_user().email()
            
    def send_generic_email(self, receiver, subject, body, sender=None):
        """ send generic email """
        if (not sender):
            sender = self.sender_email
        logging.debug("Sending mail")
        logging.debug("-- SENDER: "+sender)
        logging.debug("-- TO: "+receiver)
        logging.debug("-- SUBJECT: "+subject)
        logging.debug("-- BODY: "+body)
        mail.send_mail(sender, receiver, subject, body)
    
    def send_secret_notification(self, receiver_email):
        """ Send email notification of a secret """
        mail.send_mail(sender=self.sender_email,
              to=receiver_email,
              subject="You received a secret [SECRETS]",
              html="<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\"> <html> <head> <title>You just received a Secret</title> <meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\"> <style type=\"text/css\"> <!-- a { text-decoration: none; font-weight: bold; color:#DA8619; } --> </style> </head> <body marginheight=\"5\" marginwidth=\"5\" topmargin=\"0\" leftmargin=\"0\" > <table width=\"100%\" height=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" bgcolor=\"#FFFFCC\"> <tr> <td valign=\"top\" align=\"center\">&nbsp; <table width=\"550\" border=\"1\" cellspacing=\"0\" cellpadding=\"0\"> <tr> <td align=\"left\" style=\"padding:10px 0 15px 10px; color:#666666;\"><p class=\"style2\">Hello. I just sent you a <strong>secret</strong> -<em> encrypted message</em>.<br> <br> Please login to <a href=\"https://secrets-app.appspot.com\">Secrets</a> to decrypt and read my message.</p> <p class=\"style2\">To preserve security, in order to decrypt the message <br> you need to insert a <strong>password</strong>. <br> <br> Please ask the password directly to me if you do not know it yet.</p> <p class=\"style2\">&nbsp;</p></td> </tr> <tr> <td align=\"left\" style=\"padding:10px 0 15px 10px; font-size:11px; color:#666666;\"><strong><a href=\"https://secrets-app.appspot.com\">Secrets</a></strong> is a Web 2.0 service by <a href=\"http://www.littlelite.net/\">LittleLite Software</a>.<br> We design and develop <a href=\"http://www.littlelite.net/\">encryption and privacy related software products</a>.<br></td> </tr> </table></td> </tr> <tr><td>&nbsp;</td></tr> <tr><td>&nbsp;</td></tr> </table> </body> </html>",
              body="""
              
Hello. I just sent you a secret - encrypted message.
Please login to http://secrets-app.appspot.com to decrypt and read my message.

To preserve security, in order to decrypt the message you need to insert a password. 
Please ask the password directly to me if you do not know it yet.

To login to Secrets just copy and paste this URL into your browser:
http://secrets-app.appspot.com.

[Secrets is a Web 2.0 service by LittleLite Software]

""")

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
        registered = db.GqlQuery("SELECT * FROM SecretsUser WHERE user = :1", self.__user)
        return registered.get()
        
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
    
    





