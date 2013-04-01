""" 
 SECRETS 
 A LittleLite Web Application
 
 main.py
 
"""

import webapp2
import logging

# Select Django v.0.96
from google.appengine.dist import use_library
use_library('django', '0.96')

# Secrets Imports
from littlelite.secrets.pages import Index
from littlelite.secrets.pages import Register
from littlelite.secrets.pages import Menu
from littlelite.secrets.pages import Compose
from littlelite.secrets.pages import View
from littlelite.secrets.pages import How
from littlelite.secrets.pages import Contact
from littlelite.secrets.pages import Plugins
from littlelite.secrets.pages import Addresses
from littlelite.secrets.pages import AddressEdit
from littlelite.secrets.pages import Logout
from littlelite.secrets.pages import Profile
from littlelite.secrets.pages import AccountDeleted
from littlelite.secrets.pages import Admin

SECRETS = webapp2.WSGIApplication(
                                     [('/', Index),
                                      ('/register', Register),
                                      ('/menu', Menu),
                                      ('/compose', Compose),
                                      ('/view', View),
                                      ('/howdoesitwork', How),
                                      ('/contact', Contact),
                                      ('/plugins', Plugins),
                                      ('/addressbook', Addresses),
                                      ('/addressedit', AddressEdit),
                                      ('/loginout', Logout),
                                      ('/profile', Profile),
                                      ('/accountdeleted', AccountDeleted),
                                      ('/admin', Admin)
                                     ],
                                    debug=True)

def main():
    """ Secret's entry point """
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Welcome to Secrets.')

if __name__ == "__main__":
    main()
    
    