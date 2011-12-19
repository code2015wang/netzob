# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import base64
import logging
import StringIO

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

class TypeIdentifier():
    
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.TypeIdentifier.py')
    
    #+---------------------------------------------- 
    #| Identify the possible types from a hexa string
    #+----------------------------------------------
    def getTypes(self, stringsTable):
        entireString = "".join(stringsTable)
        
        setSpace = set()
        for i in range(0, len(entireString), 2):
            setSpace.add(int(entireString[i:i + 2], 16))
        sorted(setSpace)

        aggregatedValues = ""
        for i in setSpace:
            aggregatedValues += chr(i)

        typesList = []
        if aggregatedValues == "":
            return typesList
        if aggregatedValues.isdigit():
            typesList.append("num")
        if aggregatedValues.isalpha():
            typesList.append("alpha")
        if aggregatedValues.isalnum():
            typesList.append("alphanum")
        if self.isAscii(aggregatedValues):
            typesList.append("ascii")
        if self.isBase64(stringsTable):
            typesList.append("base64enc")
            typesList.append("base64dec")
        typesList.append("binary")

        return typesList
    
    #+---------------------------------------------- 
    #| Return True if the string parameter is ASCII
    #+----------------------------------------------
    def isAscii(self, string):
        try:
            string.decode('ascii')
            return True
        except UnicodeDecodeError:
            return False 

    #+---------------------------------------------- 
    #| Return True if the string table parameter is base64
    #|  encoded
    #+----------------------------------------------
    def isBase64(self, stringsTable):
        res = True
        try:
            for string in stringsTable:
                s = ""
                for i in range(0, len(string), 2):
                    s += chr(int(string[i:i + 2], 16))
                tmp = base64.b64decode(s)
                if tmp == "":
                    res = False
        except TypeError:
            res = False

        return res    

    
    
    #+---------------------------------------------- 
    #| Transforms "abcd" in ['0x23', 'Ox6c', ....]
    #+----------------------------------------------
    def ascii2hex(self, msg):
        return [hex(ord(x)) for x in msg] 

    #+---------------------------------------------- 
    #| Return a hexdump of a hex message
    #+----------------------------------------------          
    def hexdump(self, buf, start=0):
        length = len(buf)
        res = StringIO.StringIO()
        def GetPrintableChar(str):
            if str.isalnum():
                return str
            elif str == '\n' :
                return "<CR>"
            else:
                return '.'

        i = 0
        while i < length:
            if length - i > 16:
                l = 16
            else:
                l = length - i
            
            res.write('0x%08x  ' % (i + start))
            s = ' '.join(["%02x" % ord(c) for c in buf[i:i + l]])
            res.write(s)
            sp = 49 - len(s)
            res.write(' ' * sp)
            s = ''.join(["%s" % GetPrintableChar(c) for c in buf[i:i + l]])
            res.write(s)
            res.write('\n')
            i = i + 16

        return res.getvalue()