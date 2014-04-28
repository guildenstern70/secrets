""" 
 SECRETS 
 A LittleLite Web Application
 
 pages.py

"""

from littlelite.db.queries import UserQueries
from littlelite.secrets.utils import Folders


class Summary(object):
    """ Class to handle the summary shown in Folders view (divFolders) """
    
    def __init__(self, secretsuser):
        self.user = secretsuser
        self.inbox_count = 0
        self.sent_count = 0
        self.draft_count = 0
        self.trash_count = 0
        self.archive_count = 0
        self.__read_database()
        self.all = self.total_messages()
        
    def total_messages(self):
        """ Total messages in user box """
        return (self.inbox_count+self.sent_count+self.draft_count+self.trash_count+self.archive_count)
        
    def __read_database(self):
        """ Read the DB for messages """
        self.inbox_count = UserQueries.folder_messages_count(self.user, Folders.INBOX)
        self.sent_count = UserQueries.folder_messages_count(self.user, Folders.SENT)
        self.draft_count = UserQueries.folder_messages_count(self.user, Folders.DRAFT)
        self.trash_count = UserQueries.folder_messages_count(self.user, Folders.TRASH)
        self.archive_count = UserQueries.folder_messages_count(self.user, Folders.ARCHIVE)
        
    def status(self):
        return str(self)

    def __str__(self):
        str_summary = str(self.total_messages())
        str_summary += ' ['
        str_summary += str(self.inbox_count)
        str_summary += ','
        str_summary += str(self.sent_count)
        str_summary += ','
        str_summary += str(self.draft_count)
        str_summary += ','
        str_summary += str(self.trash_count)
        str_summary += ','
        str_summary += str(self.archive_count)
        str_summary += ']'
        return str_summary
        