# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 13:49:55 2021

@author: USER
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from lib.Log import Log
from Lib import copy


class BackgroundJob:
    def __init__(self):
        self.__id =""
        self.__type = 'interval'
        self.__interval = 0
        self.__callback = None        
    
    def setId(self, v):
        self.__id = v
    
    def getId(self):
        return self.__id

    def setType(self, v):
        self.__type = v
    
    def getType(self):
        return self.__type
    
    def setInterval(self, v):
        self.__interval = v
    
    def getInterval(self):
        return self.__interval
    
    def setCallback(self, v):
        self.__callback = v
    
    def getCallback(self):
        return self.__callback;

    @classmethod
    def build(cls, jid, sec, cbf):
        o = BackgroundJob()
        o.setId(jid)
        o.setInterval(sec)
        o.setCallback(cbf)
        return o



class BackgroundSchedulers:
    __instance = None
            
    
    def __init__(self):
        if BackgroundSchedulers.__instance is not None:
            raise Exception('BackgroundSchedulers class는 싱글톤으로 구현되었습니다. ')
        else:
            BackgroundSchedulers.__instance = self
            
            self.schedulers = {} 
            self.__schedulerProccess = BackgroundScheduler()            
            self.__schedulerProccess.start()            

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            BackgroundSchedulers()
        
        return cls.__instance
    
    
    @classmethod
    def release(cls):
        if cls.__instance is not None:
            cls.__instance.removeAll()
            cls.__instance.getSchedulerProcess().shutdown(wait=False)
            cls.__instance = None
    
    def getSchedulers(self):
        return self.schedulers
    
    def getSchedulerProcess(self):
        return self.__schedulerProccess

    
    def addJob(self, job:BackgroundJob):
        self.__schedulerProccess.add_job(job.getCallback(), job.getType(), seconds=job.getInterval(), id=job.getId())
        self.schedulers[job.getId()]= job
        #sched.remove_job("test_2")

    def removeAll(self):
        if len(self.schedulers)>0:
            for job_id in self.schedulers:
                print("BackgroundSchedulers:removeAll() ")
                self.__schedulerProccess.remove_job(job_id)        

    def removeJob(self, job_id):
        if job_id in self.schedulers:
            print("BackgroundSchedulers:removeJob "+job_id)
            del self.schedulers[job_id]
            self.__schedulerProccess.remove_job(job_id)
        
    