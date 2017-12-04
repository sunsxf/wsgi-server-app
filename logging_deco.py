#!/usr/bin/env python
# coding=utf-8
#@author sunxiongfei
from functools import wraps
import logging,time

def decorator(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        # logger = logging.getLogger()
        # fhandler = logging.FileHandler(encoding='utf-8')
        # fhandler.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # fhandler.setFormatter(formatter)
        # logger.addHandler(fhandler)
        # logger.debug('debug log')
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S')


        return func(*args,**kwargs)
    return wrapper
