""" 
 SECRETS 
 A LittleLite Web Application
 
 utils.py

"""


import random

class Alfa(object):
    """ Alfa """
    
    BETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ{} []()<>,.?;:'+-=@!#$%^&*~`_|/abcdefghijklmnopqrstuvwxyz0123456789"
    
    @staticmethod
    def get_char_at(pos):
        """ get char at specified position in the BETO string """
        len_beto = len(Alfa.BETO)
        if (pos > len_beto -1):
            pos -= len_beto
        elif (pos < 0):
            pos += len_beto  
        return Alfa.BETO[pos]
    
    @staticmethod
    def is_alfa(car):
        """ If car character in inside BETO string """
        dove = Alfa.BETO.find(car)
        if (dove < 0):
            return False
        return True
    
    @staticmethod
    def get_pos_of(car):
        """ Get the position of car inside BETO """
        return Alfa.BETO.find(car)
    
    @staticmethod
    def get_random_string(strlen=8):
        """ Get a random string. strlen is the length of the created string (default=8) """
        tmp = ''
        count = 0
        xls = 79
        rnd = random.Random()
        while (count < strlen):
            tmp += Alfa.get_char_at(rnd.randint(0, xls))
            count += 1
        return tmp
    
class Parameters(object):
    
    def __init__(self, shift, key=''):
        self._shift = shift
        self._key = key
      
    def __get_shift(self):
        return self._shift
        
    def __set_shift(self, value):
        self._shift = value
        
    def __get_key(self):
        return self._key
        
    def __set_key(self, value):
        self._key = value
        
    def get_alfa_shift(self, pos):
        """ Get the shift given the position in the alphabetic sequence """
        jpos = pos % len(self._key)
        chx = self._key[jpos]
        return Alfa.get_pos_of(chx)
        
    shift = property(fget=__get_shift, fset=__set_shift, doc='Shift')
    key = property(fget=__get_key, fset=__set_key, doc='Key')
    

class Caesar(object):
    """ Caesar Encryption """
    
    def __init__(self, parameters):
        self.shift = parameters.shift
        
    def code(self, clear_text):
        """ Perform Caesar Encryption """
        return self.algo(clear_text, decode=False)
    
    def decode(self, encrypted_text):
        """ Perform Caesar Decryption """
        return self.algo(encrypted_text, decode=True)
    
    def algo(self, text, decode=True):
        """ Caesar algorithm """
        tmp = ''
        npos = 0
        
        if (self.shift == 0):
            return text
        
        if (decode):
            self.shift = -self.shift
        
        for chx in text:
            carpos = Alfa.get_pos_of(chx)
            if (carpos >= 0):
                npos = carpos + self.shift
                tmp += Alfa.get_char_at(npos)
            else:
                tmp += chx
        
        return tmp
    
class Key(object):
    """ Key Encryption """
    
    def __init__(self, parameters):
        self._params = parameters
        
    def code(self, clear_text):
        """ Key Encryption """
        return self.algo(clear_text, decode=False)
    
    def decode(self, encrypted_text):
        """ Key Decryption """
        return self.algo(encrypted_text, decode=True)
        
    def algo(self, text, decode):
        """ Key Algorithm """
        npos = 0
        j = 0
        tmp = ''
        for chx in text:
            carpos = Alfa.get_pos_of(chx)
            if (carpos >= 0):
                if (decode):
                    npos = carpos - self._params.get_alfa_shift(j);
                else:
                    npos = carpos + self._params.get_alfa_shift(j);
                tmp += Alfa.get_char_at(npos);
            else:
                tmp += chx;
            j += 1
                
        if (self._params.shift > 0):
            caesar = Caesar(self._params)
            if (decode):
                tmp = caesar.decode(tmp)
            else:
                tmp = caesar.code(tmp)
            
        return tmp
