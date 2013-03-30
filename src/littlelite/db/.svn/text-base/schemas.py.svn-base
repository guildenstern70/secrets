""" 
 SECRETS 
 A LittleLite Web Application
 
 message.py

"""

# Google Imports
from google.appengine.ext import db

# LittleLite Imports
from littlelite.secrets.utils import Folders

class AddressBook(db.Model):
    """ DB Schema: AddressBook """
    user = db.UserProperty(required=True)
    address = db.StringProperty(required=True)
    name = db.StringProperty()

class SecretsUser(db.Model):
    """ DB Schema: SecretsUser """
    username = db.StringProperty(required=True)
    user = db.UserProperty(required=True)
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    yearbirth = db.IntegerProperty()
    added = db.DateTimeProperty(auto_now_add=True)
    receivenews = db.BooleanProperty(default=True)
    quota = db.IntegerProperty(default=100)
    #messages = Message
        
    @property
    def own_messages(self):
        return Message.all().filter('owner', self.key())

    
class Message(db.Model):
    """ DB Schema: Message """
    sender = db.EmailProperty(required=True)
    receiver = db.EmailProperty(required=True)
    owner = db.ReferenceProperty(SecretsUser, collection_name='messages', required=True)
    title = db.StringProperty()
    message = db.TextProperty()
    datetime = db.DateTimeProperty(auto_now_add=True)
    received = db.BooleanProperty()
    decrypted = db.BooleanProperty()
    algorithm = db.StringProperty()
    folder = db.StringProperty()
    
    def dump(self):
        return "%s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s" % (self.sender, self.receiver, self.owner.username, self.title, self.message[:10], self.datetime, self.received, self.decrypted, self.algorithm, self.folder)
    
    def change_folder(self, new_folder):
        """ Change message folder and update db """
        self.folder = new_folder
        self.put()
    
    def send_copy_to(self, user):
        """  Call this method when the message is received by the user """
        new_message = Message(sender=self.sender, receiver=self.receiver, owner=user)
        new_message.title = self.title
        new_message.message = self.message
        new_message.datetime = self.datetime
        new_message.received = self.received
        new_message.decrypted = self.decrypted
        new_message.algorithm = self.algorithm
        new_message.folder = Folders.INBOX
        new_message.put()
        return new_message
        


    



    
    

