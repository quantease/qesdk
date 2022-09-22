# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 17:42:01 2022

@author: ScottStation
"""
import re
from .client import qedataClient
from .utils import *
import pandas as pd
import numpy as np
import json
from datetime import datetime, date, timedelta
from .api import convert_freq,convert_security,convert_start_date,convert_end_date
from .api import is_valid_date

validExIDs = ['SSE','SZE','SFE',"INE","DCE","ZCE","CCF","SGE"]

@assert_auth
async def aio_get_price(security, start_date, end_date, freq='minute', fields=None, overnight=False, silent=False):
    '''
    Get the bar structure data.  
    security: such as \'AG2001.SFE\' 
    start_date/end_date: such as \'2010-02-01\'
    freq: \'minute\' as default frequecny. other choice: \'daily\' \'hour\'
          \'XT\' far X minutes, \'XB\' for X days.
    fields: None is default, get all fields. Or user could choose some of these fields.    
    Return : pandas.DataFrame
    '''

    freqtype = convert_freq(freq)
    if freqtype < 0:
        print(f"freq {freq} 不合法, 合法的频率设置如下：'minute','hour','daily','XT','XB'")
        return None
    security = convert_security(security)
    if security is None:
        return
    
    if freqtype == 1:
        dfcols = ['open','close','high','low','volume','money','position','upperlimit','lowerlimit','presett','preclose','settle']
    else:
        dfcols = ['open','close','high','low','volume','money']
    
    try:
        if fields :
           assert isinstance(fields,list) and len(fields) > 0, "fields 必须为list类型，并且不能为空."
           dfcols = [f for f in fields if f in dfcols]
        cols = json.dumps(dfcols)
        start_date = convert_start_date(start_date, freqtype, overnight)
        if not start_date:
            return None
        end_date = convert_end_date(end_date, freqtype, overnight)
        if not end_date:
            return None
    
           
        if len(security) >= 14:
            if security[-3:] == 'CCF':
                dbname = "options_ccf_daily" if freqtype == 1 else "options_ccf_minu"
            else:
                return pd.DataFrame()
        elif security[-3:] == 'SSE':
            dbname = "options_shg_daily" if freqtype == 1 else "options_shg_minu"
            
        elif security[-3:] == 'SGE':
            dbname = "sge_daily" if freqtype == 1 else "sge_minu"
        else:
            dbname = "futures_daily" if freqtype == 1 else "futures_minu"
        del dfcols
        return await qedataClient.instance().queryData('get_price',**locals())
    except Exception as e:
        print("aio_get_price Error:", e.__traceback__.tb_lineno,e)
        return None


@assert_auth
async def aio_get_dominant_instID(symbol, curdate=None, code='9999'):
    if not isinstance(symbol,str) :
        print('symbol必须是合法产品名称')
        return ''
    if len(symbol) > 2 or len(symbol) < 1:
        print('symbol必须是合法产品名称')
        return ''
    if curdate is None:
        curdate = datetime.today().strftime('%Y-%m-%d')
        
    if isinstance(curdate, datetime) or isinstance(curdate, date):
        curdate = curdate.strftime('%Y-%m-%d')
   
    if len(curdate) != 10 or not is_valid_date(curdate):
        print(f'日期格式不对{curdate}')
        return ''
    curdate = curdate.replace('-','')   
    symbol = symbol.upper() + code
    return await qedataClient.instance().queryData('get_dominant_instID', **locals())

@assert_auth
async def aio_get_bar_data(instids, tradingday, count=0):
    try:
        assert isinstance(instids, list),'instids 必须是合约名list'
        #tnames = [inst2tablename(inst) for inst in instids]
        if isinstance(tradingday, str):
            tday = tradingday.replace('-','')
        elif isinstance(tradingday, datetime) or isinstance(tradingday, date):
            tday = tradingday.strftime('%Ym%d')
        else:
            raise TypeError
        instids = json.dumps(instids)    
        return await qedataClient.instance().queryData('get_bar_data', **locals())    
    except Exception as e:
        print("aio_get_bar_data Error:", e.__traceback__.tb_lineno,e)
        return None
        



__all__ = []

def _collect_func_aio():
    funcs = []
    for func in globals().keys():
        if func.startswith("aio"):
            funcs.append(func)
    return funcs

__all__.extend(_collect_func_aio())

del _collect_func_aio