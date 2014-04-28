""" 
 SECRETS 
 A LittleLite Web Application
 
 message.py

"""

import logging

# LittleLite Imports
from littlelite.db.schemas import SecretsUser
from littlelite.db.schemas import AddressBook
from littlelite.db.schemas import Message
from littlelite.secrets.utils import MailAddr

# Google Imports
from google.appengine.api import users
from google.appengine.ext import db


class UserQueries(object):
    """ A common set of GQL queries """
    
    @staticmethod
    def delete_all_addresses(login):
        """ delete user addresses """
        logging.debug('Removing addresses for '+login.email)
        addrx = UserQueries.addresses(login)
        if (addrx):
            del_count = 5
            step = 20
            while (del_count > 0):
                del_count = 0
                logging.debug('Fetching next %i addresses' % step)
                fetched = addrx.fetch(step)
                for addr in fetched:
                    logging.debug('Deleting '+ addr.address)
                    addr.delete()
                    del_count += 1
            logging.debug('Done deleting addresses')
        
    @staticmethod
    def delete_all_messages(login):
        """ delete user messages """
        logging.debug('Removing messages for '+login.email)
        mexs = UserQueries.user_messages(login)
        if (mexs):
            del_count = 5
            step = 20
            while (del_count > 0):
                del_count = 0
                fetched = mexs.fetch(step)
                logging.debug('Fetching next %i messages' % step)
                for mex in fetched:
                    logging.debug('Deleting '+ mex.title)
                    mex.delete()
                    del_count += 1
            logging.debug('Done deleting messages')
    
    @staticmethod
    def delete_account(login):
        """ delete a Secret account """
        # delete all addresses
        UserQueries.delete_all_addresses(login)
        # delete all messages
        UserQueries.delete_all_messages(login)
        # delete account
        login.user.delete()
        logging.debug('Remaining users:')
        users = SecretsUser.all()
        for usr in users:
            logging.debug('-- User: '+str(usr.user.email))
        logging.debug('Account deleted')
    
    @staticmethod
    def add_address(login, email_address, name=None):
        """ add address to addressbook """
        dbuser = login.user
        googleuser = login.google_user
        dbaddress = AddressBook(parent=dbuser, user=googleuser, address=email_address)
        logging.debug('Adding address: '+email_address)
        if (name):
            dbaddress.name = name
        dbaddress.put()
        
    @staticmethod
    def delete_address(login, addrkey):
        """ delete an address from addressbook """
        address_key = db.Key(addrkey)
        address = db.GqlQuery("SELECT * "
                              "FROM AddressBook "
                              "WHERE ANCESTOR IS :1 "
                              "AND __key__=:2", login.user, address_key)
        address.get().delete()
    
    @staticmethod
    def update_address(login, addrkey, ajax_mail=None, ajax_contact=None):
        """ update an address """
        address_key = db.Key(addrkey)
        address = db.GqlQuery("SELECT * "
                              "FROM AddressBook "
                              "WHERE ANCESTOR IS :1 "
                              "AND __key__=:2", login.user, address_key)
        dbaddress = address.get()
        if (ajax_mail):
            dbaddress.address = ajax_mail
        if (ajax_contact):
            dbaddress.name = ajax_contact
        logging.debug('Updating email for '+ dbaddress.address)
        dbaddress.put()
    
    @staticmethod   
    def registered_users():
        return SecretsUser.all().count()
    
    @staticmethod
    def user_messages(login):
        """ get the messages of a user for count or delete purposes """     
        user = login.user
        messages = None
        if (user):
            messages = user.own_messages  # All messages of given user
        else:
            whereuser = str(users.get_current_user())
            logging.debug('Getting messages for user  = '+ whereuser)
            messages = Message.all().filter("user = ", whereuser)
        logging.debug('Found '+ str(messages.count()) + ' messages')
        return messages
        
    @staticmethod
    def user_messages_count(login):
        """ get the number of messages stored for the user with the given e-mail """
        return UserQueries.user_messages(login).count()
    
    @staticmethod
    def query_address(login, address_start):
        """ get a list of addresses (strings) starting with address_start """
        addresses = UserQueries.addresses(login)
        results = None
        if (addresses):
            results = [address.address for address in addresses if address_start in address.address] 
            results = results[:5]
        return results
            
    @staticmethod
    def addresses(login):
        """ get addresses in address book """  
        addresses = AddressBook.all()
        addresses.ancestor(login.user)   
        addresses.order('address')
        logging.debug('Getting addresses for ' + str(login.google_user))
        if (addresses.count() < 1):
            logging.debug('No addresses found for ' + login.username)
            addresses = None
        else:
            logging.debug('Found '+ str(addresses.count()) + ' addresses for ' + login.username)
        return addresses
         
    @staticmethod
    def folder_messages_count(user, folder):
        """ get the number of messages in one folder """
        mex_count = 0
        if (user):
            messages = user.own_messages  # All messages of given user
            messages.filter('folder', folder) # User messages in given folder
            mex_count = messages.count()
        return mex_count
        
    @staticmethod   
    def messages(login, folder):
        """ get the messages in a particular folder 
            login = login.Login object
        """
        user = login.user
        mex = None
        if (user):
            messages = user.own_messages  # All messages of given user
            messages.filter('folder', folder) # User messages in given folder
            mex = messages.order('-datetime')
        else:
            # This is the case when the datastore is not consistent
            logging.debug('Warning: datastore not CONSISTENT')
            mex = UserQueries.user_messages(login)
        return mex
            
    @staticmethod
    def is_user_registered(user_email):
        """ If the e-mail is the one of a registered user """
        searched = False
        researched_user = SecretsUser(user_email)
        user = SecretsUser.all().filter('user', researched_user)
        if (user):
            logging.debug('User '+user_email+' is registered on Secrets')
            searched = True
        return searched
    
    @staticmethod
    def secrets_waiting_for(user_email):
        """ Return the secrets (Message) waiting for the user.
            The secrets are searched in all messages with To=user_email
        """
        receiver_mail = db.Email(user_email)
        messages = Message.all().filter('receiver', receiver_mail)
        return messages.fetch(100)
        
    @staticmethod
    def initialize_user(secretsuser):
        """ Search for messages waiting for the user 
            Move those messages in the PBox of th user.
            User = SecretsUser() object """
        pending_messages = UserQueries.secrets_waiting_for(secretsuser.user.email())
        logging.debug(secretsuser.username + ' has ' + str(len(pending_messages)) + ' secrets waiting for him.')
        for msg in pending_messages:
            logging.debug('Moving message '+ msg.title +' in '+ secretsuser.username +' inbox')
            msg.send_copy_to(secretsuser)
            
    @staticmethod
    def get_dbuser(user):
        logging.debug(' > Getting db user '+str(user))
        registered = db.GqlQuery("SELECT * FROM SecretsUser WHERE user = :1", user)
        dbuser = registered.get() 
        logging.debug(' > Found db user = '+str(dbuser))
        return dbuser
            
    @staticmethod
    def get_registered_user(user_email):
        """ Get the SecretsUser object of a registered user, from email
            If user is not found, None is returned """
        email_address = MailAddr(user_email)
        researched_user = users.User(email_address.address)
        userquery = SecretsUser.all().filter('user', researched_user)
        return userquery.get()
    
    @staticmethod
    def get_message(message_key):
        """ Get a db Message object by its key """
        message_key = db.Key(message_key)
        message = db.GqlQuery("SELECT * FROM Message WHERE __key__=:1", message_key)
        return message.get()    
           
    @staticmethod
    def delete_message(login, folder, msgkey):
        """ delete a message from secret box """
        to_delete = UserQueries.get_message(msgkey)
        to_delete.delete()
        
    @staticmethod
    def message_dump():
        #message_query = db.GqlQuery("SELECT * FROM Message")
        messages = Message.all()
        logging.debug('SENDER \t RECEIVER \t OWNER \t TITLE \t MESSAGE \t DATE \t RECVD \t DECRPT \t ALGO \t FOLDER ')
        logging.debug('======================================================================================================================')
        for msg in messages:
            logging.debug(msg.dump())
        logging.debug('======================================================================================================================')
    




        