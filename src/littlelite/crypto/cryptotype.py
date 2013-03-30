""" 
 SECRETS 
 A LittleLite Web Application
 
 cryptotype.py

"""

import logging

class Algorithm(object):
    """ Algorithms enumeration """
    DES = 'des'
    THREEDES = '3des'
    AES = 'aes'
    BLOWFISH = 'blowfish'
    RC4 = 'arcfour'
    

class CryptoType(object):
    """ Wraps Crypto type """
    def __init__(self, algorithm):
        self.algo = algorithm
        if (self.algo == Algorithm.DES):
            self.description = "DES - 64 bit"
        elif (self.algo == Algorithm.THREEDES):
            self.description = "3DES - 128 bit"
        elif (self.algo == Algorithm.AES):
            self.description = "AES - 256 bit"
        elif (self.algo == Algorithm.BLOWFISH):
            self.description = "Blowfish - 448 bit"
        elif (self.algo == Algorithm.RC4):
            self.description = "ArcFour - 1024 bit"
        else:
            logging.debug('>>>WARNING: Unknown cryptotype')
            self.description = "Unknown algorithm"
            
    def id(self):
        return self.algo
                
    def __str__(self):
        return self.description
            
    @staticmethod      
    def getAvailableAlgorithms():
        return "DES - 64 bit", "3DES - 128 bit", "AES - 256 bit", "Blowfish - 448 bit"
         
