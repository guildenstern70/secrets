""" 
 SECRETS 
 A LittleLite Web Application
 
 utils.py

"""


from polycrypt import Alfa
from polycrypt import Key
from polycrypt import Parameters
from cryptotype import Algorithm, CryptoType

from pyDes import *
from pyRijndael import EncryptData, DecryptData
from blowfish import Blowfish

import hashlib
import base64
import logging

def password_to_key(stringkey):
    """ Convert a password in a sequence of bytes by applicating hash function md5 """
    return hashlib.md5(stringkey).digest()
    
class BlowfishWrapper(object):
    """ Create Blowfish crypto object """
    def __init__(self, key):
        self.name = 'blowfish'
        key_448 = self.__generate448key(key)
        self.blowfish = Blowfish(key_448)
        
    def __generate448key(self, key):
        sha512password = hashlib.sha512(key).digest()
        return sha512password[:56] # Using the first 56 bytes only (448 bits)
        
    def encrypt(self, message):
        self.blowfish.initCTR()
        return self.blowfish.encryptCTR(message)

    def decrypt(self, encrypted):
        self.blowfish.initCTR()
        return self.blowfish.decryptCTR(encrypted)
        
class AESWrapper(object):
    """ Create AES crypto object """
    def __init__(self, key):
        self.name = 'aes'
        self.plainkey = key
        
    def encrypt(self, message):
        """ Encrypt message with AES """
        logging.debug('Encrypting with %s engine' % self.name)
        return EncryptData(self.plainkey, message)
    
    def decrypt(self, encrypted):
        """ Decrypt encrypted string """
        logging.debug('Decrypting with %s engine' % self.name)
        return DecryptData(self.plainkey, encrypted)
        
        
class DESWrapper(object):
    """ Create a DES crypto object """
    
    def __init__(self, key):
        dkey = password_to_key(key)[:8] # Using the first 8 bytes only
        self.desobj = des(dkey, padmode=PAD_PKCS5)
        self.name = 'des'
    
    def encrypt(self, message):
        """ Encrypt message """
        logging.debug('Encrypting with %s engine' % self.name)
        return self.desobj.encrypt(message)
    
    def decrypt(self, encrypted):
        """ Decrypt encrypted string """
        logging.debug('Decrypting with %s engine' % self.name)
        return self.desobj.decrypt(encrypted)

class TripleDESWrapper(DESWrapper):
    """ Create a 3DES crypto object """
    def __init__(self, key): #IGNORE:W0231
        dkey = password_to_key(key)
        self.desobj = triple_des(dkey, padmode=PAD_PKCS5)
        self.name = '3des'

class CryptoWrapper(object):
    """ Create a crypto object. 
        You can create 3 encrypting engine:
        'vigenere' = a simple engine
        'des' = a DES engine
        '3des' = a TripleDES engine
        'aes' = a complex engine """
    
    def __init__(self, password, crypto_type):
        """ Parameters:
            password = string password
            crypto_type = instance of cryptotype """
        logging.debug('Initializing crypto engine %s' % crypto_type)
        cryptoid = crypto_type.id()
        
        switch = {
            'des': DESWrapper(password),
            '3des': TripleDESWrapper(password),
            'aes': AESWrapper(password),
            'blowfish': BlowfishWrapper(password)
        }
        
        if cryptoid in switch:
            self.crypto = switch[cryptoid]
            logging.debug('Ok crypto engine %s initialized.' % crypto_type)
        else:
            pass
        
    def encrypt(self, message):
        """ Encrypt a message """
        return self.crypto.encrypt(message)
    
    def decrypt(self, encrypted):
        """ Decrypt a message """
        return self.crypto.decrypt(encrypted)
    
def test_engine(key):
    """ Test engines """
    print "TEST Engines (key="+key+")\n" 
    engines = [ 'des', '3des', 'aes', 'blowfish' ]
    for engine_name in engines:
        print 'Testing engine %s ' % engine_name
        cryptotype = CryptoType(engine_name)
        engine = CryptoWrapper(key, cryptotype)
        #test(engine, codeWords)
    
def test(engine, clear_messages):
    """ Run test """
    for message in clear_messages:
        coded = engine.encrypt(message)
        decoded = engine.decrypt(coded)
        if (message == decoded):
            print "OK -> Code of " + message + " = " + base64.b64encode(coded)
        else:
            print "!!! KO -> Code of " + message + " = " + decoded + " != " + base64.b64encode(coded)
    

    
