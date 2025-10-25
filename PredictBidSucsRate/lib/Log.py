# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 11:25:22 2021

@author: USER
"""
from lib.MessageDispatcher import MessageDispatcher
from ui.sub.subLogForm import SubLogForm
import datetime as dt
import logging


class Log:
    dispatcher = MessageDispatcher.getInstance();
    
    
    def __init__(self):
        logging.basicConfig()
        logging.getLogger('Log').setLevel(logging.DEBUG)

    
    @classmethod
    def debug(cls, msg):
        id = SubLogForm.id
        strdt = dt.datetime.now().isoformat()
        
        fmtMsg = strdt+" [DEBUG] " + msg
        cls.dispatcher.send(id, cls, "log", fmtMsg)
        
        logging.debug(fmtMsg)
        
        print(fmtMsg)
        
