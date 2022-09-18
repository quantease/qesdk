# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 23:42:18 2022

@author: ScottStation
"""

import thriftpy2
import asyncio
import zlib
import pickle
import msgpack
import json
import sys
from os import getenv, path

from thriftpy2.rpc import make_aio_client
from .utils import get_mac_address
import nest_asyncio
nest_asyncio.apply()

try:
    from .config import server_config
except:
    server_config = {'host' : '127.0.0.1',
                     'port' : 6001}    



__version__='0.0.6'

thrift_path = path.join(sys.modules["ROOT_DIR"], "qedata.thrift")
thrift_path = path.abspath(thrift_path)
#print(thrift_path)
qedata_thrift = thriftpy2.load(thrift_path, module_name="qedata_thrift")
loop = asyncio.get_event_loop()
def setTimeout(client, timeout):
    try:
        try:
                sock = client._iprot.trans._trans.sock
        except AttributeError:
                sock = client._iprot.trans.sock
                sock.settimeout(timeout)
    except Exception:
        pass
   
class qedataClient(object):
    _systoken = ''
    _instance = None
    request_timeout = 30*1000
    
    def __init__(self):
        pass
    
    def __call__(self, method, **kwargs):
        #print(kwargs)
        asyncio.run(self.queryData(method, **kwargs))
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = qedataClient()
        return cls._instance    
    
    @classmethod
    def check_auth(cls):
        token = cls._systoken
        #print('auth',token)
        return token != ''
            
    
    
    async def echo(self, name):
        client = await make_aio_client(
            qedata_thrift.TestService, server_config['host'], server_config['port'])#,timeout=30*1000)
        #setTimeout(client, 30*1000)
        result = await client.echo(name)
        print(result,self._systoken)
        client.close()
    
    async def queryData(self, method, **kwargs):
        client = await make_aio_client(
            qedata_thrift.TestService, server_config['host'],  server_config['port'], timeout=self.request_timeout)
        setTimeout(client, self.request_timeout)
        req = qedata_thrift.St_Query_Req()
        req.method_name = method
        req.params = zlib.compress(msgpack.dumps(kwargs,use_bin_type=True))
        req.token=self._systoken
        #print(req.params)
        result = await client.query(req)
        
        if result.status:
            msg = result.msg
            #print(msg)
            print(pickle.loads(zlib.decompress(msg)))
        else:
            print(result.msg)
            
        client.close()
    
    @classmethod
    async def auth(cls, username, authcode):
        global systoken
        client = await make_aio_client(
            qedata_thrift.TestService, server_config['host'],  server_config['port'],timeout=cls.request_timeout)
        setTimeout(client, cls.request_timeout)
        result = await client.auth(username, authcode, True, get_mac_address(), __version__)
        #print(result)
        if result.status:
            cls._systoken = result.msg
            print('AUTH SUCCEED')
        else:
            print(f'AUTH FAILED : {result.msg}')
            
        client.close()
    
def auth(username, authcode):
    asyncio.run(qedataClient.auth(username, authcode))
    
    
def testClient():
    #loop.run_until_complete(qedataClient.instance().auth('quantease','$1$$k7yjPQKv8AJuZERDA.eQX.'))
    asyncio.run(qedataClient.instance().echo('test'))
