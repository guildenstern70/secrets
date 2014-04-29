""" 
 SECRETS 
 A LittleLite Web Application
 
 pages.py

"""
import webapp2

import logging
import base64
import sys
import urllib

# Google Imports
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import urlfetch

# Django Imports
from django.utils import simplejson
from django.core.paginator import Paginator

# LittleLite Imports
from littlelite.secrets.utils import Folders
from littlelite.secrets.login import Login
from littlelite.crypto.cryptwrapper import CryptoWrapper
from littlelite.crypto.cryptotype import CryptoType
from littlelite.secrets.utils import Mailer
from littlelite.secrets.summary import Summary
from littlelite.db.schemas import SecretsUser
from littlelite.db.schemas import Message
from littlelite.db.queries import UserQueries

# Global variables
IMAGE = 0
VERSION_MAJOR = 0
VERSION_MINOR = 14
VERSION_BUILD = 1024

def version():
    """ Secrets version """
    return str(VERSION_MAJOR)+"."+str(VERSION_MINOR)+"."+str(VERSION_BUILD)

def login_required(func):
    """ Login required wrapper """
    def wrapper(self, *args, **kw):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            func(self, *args, **kw)
    return wrapper
    
class Profile(webapp2.RequestHandler):
    """ /profile page """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
    
    @login_required
    def get(self): #IGNORE:C0111   
        template_values = {
            'login': self.login,
            'user': self.login.user
        }
        self.response.out.write(template.render('templates/profile.html', template_values))
         
    def post(self): #IGNORE:C0111 
        command = self.request.get('command') 
        if (command == 'Delete my account'):
            # Deleting the account
            logging.debug('Deleting account for '+ self.login.email)
            UserQueries.delete_account(self.login)
            self.redirect(users.create_logout_url('/accountdeleted'))
        elif (command == 'Remove all messages' ):
            logging.debug('Deleting all messages for '+ self.login.email)
            UserQueries.delete_all_messages(self.login)
            self.redirect('/')
        elif (command == 'Submit'):
            #new_quota = self.request.get('newquota')
            receive_news = self.request.get('agree')
            logging.debug('Receive news: '+receive_news)
            secret_user = self.login.user
            #secret_user.quota = int(new_quota)
            if (receive_news == 'on'):
                secret_user.receivenews = True
            else:
                secret_user.receivenews = False
            secret_user.put()    
            self.redirect('/profile')
            
class AccountDeleted(webapp2.RequestHandler): 
    """ /accountdeleted page """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    def get(self): #IGNORE:C0111  
        template_values = {
            'login': self.login,
            'message': 'Your account has been deleted.'
        }
        self.response.out.write(template.render('templates/message.html', template_values)) 
           

class Admin(webapp2.RequestHandler): 
    """ /menu page """
    
    class UserMail(object):
        def __init__(self, usrobj, summaryobj):
            self.user = usrobj
            self.summary = summaryobj   
        
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    def __secret_users(self, users, lastitem):
        ss = []
        users_fetched = users.fetch(10, lastitem)
        for usr in users_fetched:
            ss.append(Admin.UserMail(usr, Summary(usr)))
        return ss
    
    def get(self): #IGNORE:C0111               
        registered = UserQueries.registered_users()   
        last_str = self.request.get('last')
        if (len(last_str)>0):
            lastitem = int(last_str)
        else:
            lastitem = 0
        secret_users = self.__secret_users(SecretsUser.all().order('-added'), lastitem) 
        items_shown = len(secret_users) 
        prev_page = lastitem - items_shown
        if (prev_page < 0):
            prev_page = 0
        next_page = lastitem + items_shown
        if (next_page > registered):
            next_page = lastitem
        template_values = {
            'login': self.login,
            'registered': registered,
            'scrt_users': secret_users,
            'prev_link': 'admin?last='+str(prev_page),
            'next_link': 'admin?last='+str(next_page)
          }
        self.response.out.write(template.render('templates/admin.html', template_values))

class Menu(webapp2.RequestHandler): 
    """ /menu page """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    def __move_messages(self, target_folder):
        """ Change message(s) folder """
        checked_items = self.request.get_all('xssl')
        for item in checked_items:
            logging.debug('Moving ' + item + ' to '+target_folder)
            UserQueries.get_message(item).change_folder(target_folder)
        
    def __compose(self):
        """ Compose a new message """
        logging.debug('Compose new message')
        self.redirect('/compose')
    
    def __delete(self):
        """ Delete one or more message(s) """
        logging.debug('Delete message')
        folder = self.request.get('whatFolder')
        if (folder == Folders.TRASH):
            self.__shred(folder)
        else:
            self.__move_messages(Folders.TRASH)
            self.redirect('/menu?folder=' + folder)
        
    def __shred(self, folder = None):
        """ Delete one or more messages from db """
        logging.debug('Shredding message')
        if (not folder):
            folder = self.request.get('whatFolder')
        checked_items = self.request.get_all('xssl')
        for item in checked_items:
            logging.debug('Deleting message ' + item + ' from db')
            UserQueries.delete_message(self.login, folder, item)
        self.redirect('/menu?folder=' + folder)

    def __archive(self):
        """ Archive one or more message(s) """
        logging.debug('Archiving message')
        original_folder = self.request.get('whatFolder')
        self.__move_messages(Folders.ARCHIVE)
        self.redirect('/menu?folder=' + original_folder)
      
    @login_required          
    def get(self): #IGNORE:C0111  
                
        folder = self.request.get('folder')
        if (not folder):
            folder = 'inbox'
        page_str = self.request.get('page')
        page = 1
        if (page_str):
            page = int(page_str) + 1
        logging.debug("Requesting menu page "+str(page))
        
        messages = UserQueries.messages(self.login, folder)                     
        paginator = Paginator(messages, 10)      
        msgcount = messages.count()
        logging.debug("There are " + str(msgcount) + " messages in " + folder + " folder.")
        if (msgcount < 1):
            messages = None
                
        paginator_page = paginator.page(page)
            
        template_values = {
            'login': self.login,
            'summary': Summary(self.login.user),
            'folder' : folder,
            'paginator': paginator,
            'page': page,
            'total_pages': paginator.num_pages,
            'messages' : paginator_page,
            'has_previous' : paginator_page.has_previous,
            'has_next' : paginator_page.has_next,     
            'has_pages' : (paginator.num_pages > 1),
            'previous' : page-1,
            'next' : page+1,
            'version': version()
          }
        self.response.out.write(template.render('templates/menu.html', template_values))
                
    def post(self):
        command = self.request.get('mode')   
        logging.debug('Menu post with command = '+command)  
        if (command[:2] == 'mt'):
            original_folder = self.request.get('whatFolder')
            if (command == 'mt_inbox'):
                self.__move_messages(Folders.INBOX)
            elif (command == 'mt_archive'):
                self.__move_messages(Folders.ARCHIVE)
            elif (command == 'mt_trash'):
                self.__move_messages(Folders.TRASH)
            self.redirect('/menu?folder=' + original_folder)
        else:
            switch = {
               'compose': self.__compose,
               'delete': self.__delete,
               'shred': self.__shred,
               'archive': self.__archive,
            }       
            if command in switch:
                switch[command]()
            else:
                logging.debug('Unknown command: '+command)

class How(webapp2.RequestHandler):
    """ /how page """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    def get(self):
        template_values = {
            'login': self.login,
            'version': version()
          }
        self.response.out.write(template.render('templates/howdoesitwork.html', template_values))
        
class Plugins(webapp2.RequestHandler):
    """ /plugins page """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    def get(self):
        template_values = {
            'login': self.login,
            'version': version()
          }
        self.response.out.write(template.render('templates/plugins.html', template_values))
                
class Contact(webapp2.RequestHandler):
    """ /contact page """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    def __send_contact_mail(self):
        correctly_sent = False
        try:
            mail_obj = Mailer()
            email = self.request.get('email')
            body = self.request.get('message')
            subject = "[SECRETS] Message: " + self.request.get('subject')
            mail_obj.send_generic_email('alessiosaltarin@gmail.com', subject, body, sender=email)
            correctly_sent = True
        except:
            logging.debug("Unexpected error in sending contact mail: " + sys.exc_info()[0])
            
        return correctly_sent
        
    def __verifyCaptcha(self, challenge, response):
        
        captchaOk = False
        
        logging.debug('Verifying catphca: ch='+challenge+', response='+response)
        captcha_fields = {
          "privatekey": "6LdOHsUSAAAAAFo4BMZz1Ob-IAIVwnXeCl8LULH6",
          "remoteip": "209.85.147.141",
          "challenge": challenge,
          "response": response
        }
        form_data = urllib.urlencode(captcha_fields)
        logging.debug('Calling recaptcha google site...')
        result = urlfetch.fetch(url='http://www.google.com/recaptcha/api/verify',
                                payload=form_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if result.status_code == 200:
            logging.debug('...done. Result was '+result.content)
            if (result.content.startswith('true')):
                captchaOk = True
        else:
            logging.debug('... error code = ' +str(result.status_code))
            
        return captchaOk
 
    def get(self):   
        mailsent = self.request.get('mailsent')
        template_values = {
            'login': self.login,
            'mailsent': mailsent,
            'version': version()
          }
        self.response.out.write(template.render('templates/contact.html', template_values))
        
    def post(self):
        
        mailSent = False
        
        # First, check recaptcha
        challenge = self.request.get('challenge')
        response = self.request.get('response')
        if (len(response) > 0 or len(challenge) > 0):
            mailSent = self.__verifyCaptcha(challenge, response)
        else:
            logging.debug('Challenge or Response is empty...')
            
        # Second, if OK send mail
        if (mailSent):
            self.redirect('/contact?mailsent=1')
        else:
            self.redirect('/contact?mailsent=0')
            
class Logout(webapp2.RequestHandler):
    """ /logout page handles logouts """
    def post(self):
        command = self.request.get('command')
        if (command == 'logout'): # logout command
            logout = users.create_logout_url("/")
            self.redirect(logout)
        elif (command == 'login'):
            self.redirect(users.create_login_url("/"))
        elif (command == 'Register'):
            self.redirect("/register")
        else:
            logging.debug('Unknown login-logout command: '+command)
            self.redirect(users.create_login_url("/"))
                   
class View(webapp2.RequestHandler):
    """ /view page """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    # Weird chrome fix
    def __clean_request(self):
        logging.debug('Dirty req: '+self.request.body)
        clean = urllib.unquote(self.request.body)
        if (clean[-1] != ']'):
            closed_bracket_idx = clean.rfind(']') + 1
            if (closed_bracket_idx > 1):
                clean = clean[:closed_bracket_idx]
        return clean
        
    def __decrypt_and_view(self, password, encrypted_msg, algo):
        logging.debug('Decrypting message')
        logging.debug("Password: "+password)
        crypto_engine = CryptoWrapper(password, CryptoType(algo))
        try:
            message = base64.b64decode(encrypted_msg) # get bytes
            clear_bytes = crypto_engine.decrypt(message)
            clear = clear_bytes.decode('UTF-8')
            if (len(clear) == 0):
                clear = '[SECRETS: Wrong password]'
        except:
            logging.debug('Error in decrypting message')
            clear = '[SECRETS: Wrong password]'
        return clear
    
    def __redirect_to_compose(self, subject, receiver, message):
        template_values = {
            'login': self.login,
            'summary': Summary(self.login.user),
            'compose_receiver': receiver,
            'compose_message': message,
            'compose_subject': subject,
            'form_action' : 'compose'
        }
        self.response.out.write(template.render('templates/compose.html', template_values))
    
    @login_required    
    def get(self):
        message_id = self.request.get('mk')
        folder = self.request.get('folder')
        message_to_view = UserQueries.get_message(message_id)
        if (not message_to_view.received):
            logging.debug('This message is read for the first time.')
            message_to_view.received = True
            message_to_view.put()
        logging.debug("Message :"+message_to_view.message[:10])
        message_content = message_to_view.message
        encryption_level = CryptoType(message_to_view.algorithm)
        logging.debug('Encryption level: '+encryption_level.description)
        template_values = {
            'login': self.login,
            'folder': folder,
            'summary': Summary(self.login.user),
            'message': message_to_view,
            'message_content': message_content,
            'encryption_level': encryption_level.description,
            'form_action': 'view',
            'version': version()
          }
        self.response.out.write(template.render('templates/compose.html', template_values))
    
    def post(self):
        mode = self.request.get('mode')
        folder = self.request.get('folder')
                    
        if (mode == 'reply'):
            subject = "RE: "+ self.request.get('subject')
            receiver = self.request.get('sender')
            if (folder == Folders.SENT):
                receiver = self.request.get('receiver')
            logging.debug("Sending reply to "+receiver)
            message = "\n\n\n=======================\nORIGINAL SECRET MESSAGE: \n" + self.request.get('message')
            self.__redirect_to_compose(subject, receiver, message)
        elif (mode == 'decryptdraft'):
            subject = self.request.get('subject')
            receiver = self.request.get('receiver')
            logging.debug("Restoring draft message")
            message = self.request.get('message')
            password = self.request.get('secretPassword')
            message = self.__decrypt_and_view(password, message, 'des')
            self.__redirect_to_compose(subject, receiver, message)
        elif (mode == 'delete'):
            item = self.request.get('key')
            logging.debug('Deleting message ' + item)
            UserQueries.get_message(item).change_folder(Folders.TRASH)
            self.redirect('/menu?folder='+Folders.INBOX)
        elif (mode == 'shred'):
            item = self.request.get('key')
            logging.debug('Shredding message ' + item)
            UserQueries.delete_message(self.login, folder, item)
            self.redirect('/menu?folder='+Folders.INBOX)
        elif (mode == 'archive'):
            item = self.request.get('key')
            logging.debug('Archiving message ' + item)
            UserQueries.get_message(item).change_folder(Folders.ARCHIVE)
            self.redirect('/menu?folder='+Folders.INBOX)
        elif (mode == 'forward'):
            subject = "FW: "+ self.request.get('subject')
            receiver = None
            logging.debug("Preparing forward")
            message = "\n\n\n=======================\nORIGINAL SECRET MESSAGE: \n" + self.request.get('message')
            self.__redirect_to_compose(subject, receiver, message)
        else:   # decrypt command AJAX request
            out_message = ""
            try:
                clean_request = self.__clean_request()
                logging.debug('Request body is %s' % clean_request)
                args = simplejson.loads(clean_request)
                encrypted_message = args[0]
                password = args[1]
                algorithm = args[2]
                result = self.__decrypt_and_view(password, encrypted_message, algorithm)
                out_message = simplejson.dumps(result)
            except:
                logging.debug(">>> Exception %s" % sys.exc_info()[0])
                out_message = '[Unable to parse input message]'
            finally:
                self.response.out.write(out_message)
  
class Compose(webapp2.RequestHandler):
    """ /compose page """

    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
    
    @login_required    
    def get(self):
        template_values = {
            'login': self.login,
            'summary': Summary(self.login.user),
            'message' : None,
            'version': version()
          }
        self.response.out.write(template.render('templates/compose.html', template_values))
        
    def __send_message(self, receiver_email, secret_message):
        logging.debug('Sending message to '+receiver_email)
        # Send email notification
        mail_obj = Mailer()
        mail_obj.send_secret_notification(receiver_email)
        # Is receiver registered
        registered_user = UserQueries.get_registered_user(receiver_email)
        if (registered_user): 
            logging.debug("User " + receiver_email + " is registered on Secrets.")
            secret_message.send_copy_to(registered_user)
            logging.debug("Message has been sent to "+registered_user.username)
        else:
            logging.debug('User is not registered on Secrets. He will find the message on first login.')
            
    def __save_secret(self, receiver, encrypted_message, encryption_method, folder):
        sender_email = db.Email(self.login.email)
        secret = Message(sender=sender_email, receiver=receiver, owner=self.login.user)
        secret.title = self.request.get('subject')
        secret.message = db.Text(encrypted_message)
        secret.algorithm = encryption_method
        secret.received = False
        secret.decrypted = False
        secret.folder = folder
        secret.put()  
        return secret
    
    def __save_email_address(self, email_address):
        addresses = UserQueries.addresses(self.login)
        if (addresses):
            if not (addresses.filter('address =', email_address).get()):
                UserQueries.add_address(self.login, email_address, None)
            else:
                logging.debug('Address '+email_address+' is already in the addressbook')
        else:
            UserQueries.add_address(self.login, email_address, None)
            
    def __encrypt(self, encryption_method):
        """ Encrypt message """
        cryptotype = CryptoType(encryption_method)
        logging.debug("Encryption Method: %s " % cryptotype)
        crypto_password = self.request.get('secretPassword')
        logging.debug("Encryption Password: "+crypto_password)
        crypto_engine = CryptoWrapper(crypto_password, cryptotype)
        unicode_message = self.request.get('message')
        encrypted_message = crypto_engine.encrypt(unicode_message.encode('UTF-8'))
        return base64.b64encode(encrypted_message)
    
    def __create_secret(self, receiver_email, folder):
        """ Create a new Message object, store it, add email of receiver if necessary """
        encryption_method = self.request.get('encryptionmethod')
        encrypted_message = self.__encrypt(encryption_method)
        self.__save_email_address(receiver_email)        
        return self.__save_secret(receiver_email, encrypted_message, encryption_method, folder)
        
    def __save_as_encrypted_draft(self):
        """ Save a secret in draft """
        receiver_email = db.Email(self.request.get('receiver'))
        self.__create_secret(receiver_email, Folders.DRAFT)   
        
    def __encrypt_and_send(self):
        """ Encrypt the message and send it """
        receiver_email = db.Email(self.request.get('receiver'))
        secret = self.__create_secret(receiver_email, Folders.SENT)        
        self.__send_message(receiver_email, secret)
                
    def post(self):
        submit_text = self.request.get('mode')
        logging.debug('Posting to /compose ['+submit_text+']')
        if (submit_text == 'compose'):
            self.__encrypt_and_send()
            target = Folders.INBOX
            msg = urllib.quote_plus("Message encrypted and sent")
        else:
            self.__save_as_encrypted_draft()
            target = Folders.DRAFT
            msg = urllib.quote_plus("Message saved as draft")
        self.redirect('/menu?folder='+target+'&msg='+msg)
        
class Register(webapp2.RequestHandler):
    """ /register page """
    
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
                 
    def get(self):
        years = range(1998, 1920, - 1)
        template_values = {
            'years': years,
            'your_messages': UserQueries.secrets_waiting_for(self.login.email),
            'user_email' : self.login.email,
            'username': self.login.username,
            'version': version()
          }
        self.response.out.write(template.render('templates/register.html', template_values))
        
    def post(self):
        
        # Get parameters
        name_of_user = self.request.get('firstname')
        lastname_of_user = self.request.get('lastname')
        birth_year = self.request.get('birth')  
        agreement = self.request.get('agree')
        
        # Save registration data
        registration_data = SecretsUser(username=name_of_user, user=users.get_current_user())
        registration_data.firstname = name_of_user
        registration_data.lastname = lastname_of_user
        registration_data.yearbirth = int(birth_year)       
        if (agreement == 'on'):
            registration_data.receivenews = True
        else:
            registration_data.receivenews = False
        registration_data.put()
        
        # Move existing messages in user's inbox
        if (self.login.user != None):
            UserQueries.initialize_user(self.login.user)
        # Log in
        msg = urllib.quote_plus("HINT:   Click 'Compose' to send an encrypted message.")
        self.redirect("/menu?folder=inbox&msg="+msg)
                
class AddressEdit(webapp2.RequestHandler):
    """ /ajax helper class for address editing """
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
    
    def post(self):
        logging.debug('Received post.')
        idaddress = self.request.get('id')
        field = self.request.get('field')
        value = self.request.get('value')
        logging.debug('Id = '+ idaddress)
        logging.debug('Field = '+ field)
        logging.debug('Value = '+ value)
        if (field == 'name'):
            UserQueries.update_address(self.login, idaddress, None, value)
        elif (field == 'email'):
            UserQueries.update_address(self.login, idaddress, value, None)
        self.response.out.write(value);   
             
class Addresses(webapp2.RequestHandler):
    """ /addressbook page """
    
    def __init__(self, request, response):
        self.initialize(request, response)
        self.login = Login()
        
    def __build_json_answer(self, query, results):
        result_json = "{ query:'" + query + "'," 
        result_json += ' suggestions:['
        for result in results:
            result_json += "'%s'," % result
        return result_json[:-1] + '] }'
        
    def get(self):
        if (self.request.get('json')):
            logging.debug('Entering AJAX path...')
            clean_request = self.request.get('query')
            request_len = len(clean_request)
            logging.debug('Request input is %s' % clean_request)
            # Query DB if request is a small number of characters...
            if (request_len > 0 and request_len < 7):
                results = UserQueries.query_address(self.login, clean_request)
                if (results):
                    result_json = self.__build_json_answer(clean_request, results)
                    logging.debug('JSON answer: %s' % result_json)
                    self.response.out.write(result_json)
        else:
            addresses = UserQueries.addresses(self.login)
            template_values = {
                'login': self.login,
                'addresses' : addresses,
                'version': version()
            }
            self.response.out.write(template.render('templates/addressbook.html', template_values))
        
    def post(self):
        # Save registration data
        mode = self.request.get('mode')
        if (mode == 'add'):
            form_name =  self.request.get('namex')
            form_address = self.request.get('emailaddr')
            logging.debug('Creating entry for %s (%s)' % (form_name, form_address))
            UserQueries.add_address(self.login, form_address, form_name)
        elif (mode == 'delete'):
            logging.debug('Deleting address(es)')
            checked_items = self.request.get_all('chkid')
            for item in checked_items:
                logging.debug('Deleting ' + item)
                UserQueries.delete_address(self.login, item)
        self.redirect("/addressbook")
    
class Index(webapp2.RequestHandler):
    """ /index page """
    
    def get(self):
        login = Login()
        logging.info("Login: " + str(login))
        
        action = self.request.get('action')
                    
        template_values = {
            'login': login,
            'version': version()
        }
                
        if (not login.is_logged):
            self.response.out.write(template.render('templates/index.html', template_values))
        else:
            if (login.is_first_time()):
                self.redirect("/register")
            elif (action == 'home'):
                self.response.out.write(template.render('templates/index.html', template_values))
            else:
                self.redirect('/menu?folder='+Folders.INBOX)            

            
