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
    from .config import outside_server_config, second_server_config
    avail_servers = [outside_server_config, second_server_config]
    server_config = avail_servers[0]
    server_index = 0
except ImportError:
    server_config = {'host' : '192.168.123.199',
                     'port' : 6001}  
    


__version__='0.1.6'

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
    _syssmtoken = ''
    _instance = None
    request_timeout = 30*1000
    
    def __init__(self):
        pass
    
    def __call__(self, method, **kwargs):
        #print(method)
        #print(kwargs)
        #print(self._syssmtoken)
        return asyncio.run(self.queryData(method, **kwargs))
    
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
            
    @classmethod
    def check_login(cls):
        smtoken = cls._syssmtoken
        #print('auth',token)
        return smtoken != ''
    
    
    async def echo(self, name):
        client = await make_aio_client(
            qedata_thrift.TestService, server_config['host'], server_config['port'])#,timeout=30*1000)
        #setTimeout(client, 30*1000)
        result = await client.echo(name)
        print(result,self._systoken)
        client.close()
    
    async def queryData(self, method, **kwargs):
        try:
            client = await make_aio_client(
                qedata_thrift.TestService, server_config['host'],  server_config['port'], timeout=self.request_timeout)
        except Exception as e:
            if len(avail_servers) > 1:
                server_index = (server_index + 1) % len(avail_servers)
                server_config = avail_servers[server_index]
                client = await make_aio_client(qedata_thrift.TestService, server_config['host'],  server_config['port'], timeout=self.request_timeout)
            else:
                return f'ERROR: {e}'
        #print('qeryData')
        try:
            setTimeout(client, self.request_timeout)
            req = qedata_thrift.St_Query_Req()
            req.method_name = method
            req.params = zlib.compress(msgpack.dumps(kwargs,use_bin_type=True))
            if "sm_get" in method:
                req.token = self._syssmtoken
            else:    
                req.token=self._systoken
            #print('token',req.token)
            result = await client.query(req)
            
            client.close()
            if result.status:
                msg = result.msg
                #print(msg)
                return(pickle.loads(zlib.decompress(msg)))
            else:
                return(result.msg)
        except Exception as e:
            return f'ERROR: {e}'
            
    @classmethod
    async def login(cls, username, password):
        try:
            client = await make_aio_client(
                qedata_thrift.TestService, server_config['host'],  server_config['port'],timeout=cls.request_timeout)
        except Exception as e:
            if len(avail_servers) > 1:
                server_index = (server_index + 1) % len(avail_servers)
                server_config = avail_servers[server_index]
                client = await make_aio_client(qedata_thrift.TestService, server_config['host'],  server_config['port'],timeout=cls.request_timeout)
            else:
                return f'ERROR: {e}'
        try:                
            setTimeout(client, cls.request_timeout)
            result = await client.login(username, password, get_mac_address(), __version__)
            #print(result)
            client.close()
            if result.status:
                cls._syssmtoken = result.msg
                print(result.msg, cls._syssmtoken)
                print('LOGIN SUCCEED')
                return True
            else:
                print(f'LOGIN FAILED : {result.msg}')
                return False
        except Exception as e:
            return f'ERROR: {e}'    
    
    @classmethod
    async def auth(cls, username, authcode):
        try:
            client = await make_aio_client(
                qedata_thrift.TestService, server_config['host'],  server_config['port'],timeout=cls.request_timeout)
        except Exception as e:
            if len(avail_servers) > 1:
                server_index = (server_index + 1) % len(avail_servers)
                server_config = avail_servers[server_index]
                client = await make_aio_client(qedata_thrift.TestService, server_config['host'],  server_config['port'],timeout=cls.request_timeout)
            else:
                return f'ERROR: {e}'
        try:                
            setTimeout(client, cls.request_timeout)
            result = await client.auth(username, authcode, False, get_mac_address(), __version__)
            #print(result)
            client.close()
            if result.status:
                cls._systoken = result.msg
                print('AUTH SUCCEED')
                return True
            else:
                print(f'AUTH FAILED : {result.msg}')
                return False
        except Exception as e:
            return f'ERROR: {e}'                
                

            
    
def auth(username, authcode):
    return asyncio.run(qedataClient.auth(username, authcode))

def login(username, password):
    return asyncio.run(qedataClient.login(username, password))

def check_auth():
    return qedataClient.check_auth()
    
    
def testClient():
    #loop.run_until_complete(qedataClient.instance().auth('quantease','$1$$k7yjPQKv8AJuZERDA.eQX.'))
    asyncio.run(qedataClient.instance().echo('test'))
