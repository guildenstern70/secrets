""" 
 SECRETS 
 A LittleLite Web Application
 
 main.py
 
"""
import logging

# Google Imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

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

SECRETS = webapp.WSGIApplication(
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
                                    debug=False)

def main():
    """ Secret's entry point """
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(SECRETS)

if __name__ == "__main__":
    main()
