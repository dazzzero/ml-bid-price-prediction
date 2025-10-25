# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:19:37 2021

@author: USER
"""
class EventNames:
    COMPLETE = "COMPLETE"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR= "ERROR"
    TERMINATED = "TERMINATED"

class BaseDispatcher:
    def __init__(self):
        self.__listeners = {}
    
    
    def __getListener(self, eventName:str):
        if eventName in self.__listeners:
            return self.__listeners[eventName]
        else:
            return None
    
    def __setListener(self, eventName:str, listener):
        if eventName in self.__listeners:
            self.__listeners[eventName].append(listener)
        else:
            self.__listeners[eventName] = []
            self.__listeners[eventName].append(listener)
            
    def dispatchEvent(self, eventName, param):
        listeners = self.__getListener(eventName)
        if listeners is not None:
            for listener in listeners:
                try:
                    listener(param)
                except Exception as e:
                    print("리스너객체를 호출하는중 에러가 발생하였습니다.\n"+format(e))            
                
    def addListener(self,eventName:str, callback):
        self.__setListener(eventName, callback)

    def removeListener(self,eventName:str, callback):
        if eventName in self.__listeners:
            ary = self.__listeners[eventName]
            ary.remove(callback)
        
    
class Telegram:
    def __init__(self):
        self.event_name =""
        self.event_param = []
        self.sender = None
        self.receiver = None
    
    def getEventName(self):
        return self.event_name
    
    def setEventName(self, v):
        self.event_name = v
    
    def getParam(self):
        return self.event_param
    
    def setParam(self, v):
        self.event_param = v
        
    def setSender(self, v):
        self.sender = v

    def getSender(self):
        return self.sender

    def setReceiver(self, v):
        self.receiver = v
    
    def getReceiver(self):
        return self.receiver
    
    @classmethod
    def build(cls, evtnm, evtparam, sender, receiver):
        c = Telegram()
        c.setEventName( evtnm )
        c.setParam( evtparam )
        c.setSender(sender)
        c.setReceiver(receiver)
        
        return c

    

class MessageDispatcher:
    __instance = None
    #clients = {}
    
    def __init__(self):
        if MessageDispatcher.__instance is not None:
            raise Exception('MessageDispatcher class는 싱글톤으로 구현되었습니다. ')
        else:
            MessageDispatcher.__instance = self
            self.clients = {}

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            MessageDispatcher()
        
        return cls.__instance


    def register(self, receiverName, callback):
        if receiverName not in self.clients:
            self.clients[receiverName] = callback
    
    def unregister(self, receiverName):
        if receiverName in self.clients:
            del self.clients[receiverName]
    
    def send(self, receiverName, sender, eventName, param):
        if receiverName in self.clients:
            
            try:
                telegram = Telegram.build(eventName, param, sender, receiverName)
                #(self.clients[receiverName])(eventName, param)
                (self.clients[receiverName])(telegram)
            except Exception as e:
                print("MessageDispatcher:send() ")
                print(e)
                

    def broadcast(self, sender, eventName, param):
        
        for key in self.clients.keys():
            try:
                telegram = Telegram.build(eventName, param, sender, None)
                (self.clients[key])(telegram)
                #(self.clients[key])(eventName, param)
            except Exception as e:
                print("MessageDispatcher:broadcast() ")
                print(e)


