# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 23:42:18 2022

@author: ScottStation
"""
import re
from .client import qedataClient
from .utils import assert_auth, get_mac_address
import pandas as pd
import numpy as np
import json
from datetime import datetime, date, timedelta

validExIDs = ['SSE','SZE','SFE',"INE","DCE","ZCE","CCF","SGE","GFE"]

def convert_security(security):
    insts = security.split('.')
    if len(insts) > 1 and insts[1] in validExIDs:
        return security.replace('.','_').upper().replace('(T+D)','_T_D').replace('-', '_')
    else:
        print(f'合约名称 {security} 不合法')

def convert_start_date(start_date, freqtype=0, overnight=False):
    if isinstance(start_date,datetime) or isinstance(start_date,date):
        if freqtype == 1:
            start_dt =  start_date.strftime('%Y%m%d')
        else:
            start_date = start_date.strftime('%Y%m%d%H%M%S')
            start_dt = start_date if freqtype==0 else start_date+ '000'
    elif isinstance(start_date, str):
        try:
            if freqtype == 1:
                start_dt =  start_date[:10].replace('-','')
            else:
                if len(start_date) == 10:
                    start_date =  start_date.replace('-','')
                    start_date += '090000' if overnight else '000000'
                elif len(start_date) == 16:
                    start_date = start_date.replace('-','').replace(':','').replace(' ','') + '00'
                elif len(start_date) == 19:    
                    start_date = start_date.replace('-','').replace(':','').replace(' ','')
                else:
                    raise ValueError
                start_dt = start_date if freqtype == 0 else start_date+'000'
            #print(start_date, start_dt)
        except ValueError:
            print('起始日期格式不对, 参考："2015-01-01"/ "2015-01-01 09:00" /"2015-01-01 09:00:00" ')
            return None
    else:
        print("起始日期应该是str或者datetime类型")
        return None
    return int(start_dt)

    
def convert_end_date(end_date, freqtype=0, overnight=False):
    if isinstance(end_date,datetime) or isinstance(end_date,date):
        if freqtype != 1:
            end_date = end_date.strftime('%Y%m%d%H%M%S')
            end_dt = int(end_date) if freqtype == 0 else int(end_date + '000')
        elif isinstance(end_date,datetime):
            end_dt =  int(end_date.strftime('%Y%m%d'))
            if end_date.hour >= 16:
                end_dt += 1
        else:
            end_dt =  int(end_date.strftime('%Y%m%d'))
        #end_dt = int(end_date.strftime('%Y%m%d%H%M%S')) if freqtype == 0 else int(end_date.strftime('%Y%m%d'))
        #print(end_dt)
    
    elif isinstance(end_date, str):
        try:
            if freqtype == 1:
                if len(end_date) == 10:
                    end_dt = int(end_date[:10].replace('-',''))
                elif len(end_date) == 16 or len(end_date) == 19:    
                    end_dt = int(end_date[:10].replace('-',''))
                    if int(end_date[11:13]) >= 16:
                        end_dt += 1
                else:
                    raise ValueError
                
            else:
                if len(end_date) == 10:
                    end_date = end_date.replace('-','')
                    end_date += '150001' if overnight else '000000'
                elif len(end_date) == 16:
                    end_date = end_date.replace('-','').replace(':','').replace(' ','') + '00'
                elif len(end_date) == 19:    
                    end_date = end_date.replace('-','').replace(':','').replace(' ','')

                else:
                    raise ValueError
                end_dt = int(end_date) if freqtype==0 else int(end_date+'000')        
            #print(start_date, start_dt)
        except ValueError:
            print('结束日期格式不对, 参考："2015-01-01"/ "2015-01-01 09:00" /"2015-01-01 09:00:00" ')
            return None
    else:
        print("结束日期应该是str或者datetime类型 ")
        return None
    return end_dt
    

def to_date_str(date):
    return str(date)

def convert_freq(freq):
    validFreqs = ['minute','hour']
    validDFreqs = ['daily']
    if freq in validFreqs:
        return 0
    elif freq in validDFreqs:
        return 1
    elif re.match(r'\d+B',freq, 0):
        return 1
    elif re.match(r'\d+T',freq, 0):
        return 0
    else:
        return -1

@assert_auth
def get_ticks(security, start_date, end_date, count=None, fields=None, overnight=False, silent=False):
    '''
    Get the tick data.  
    security: such as \'AG2001.SFE\' 
    start_date/end_date: such as \'2010-02-01\'
    count: list count=N records, if it is not None. The \'end_date\' has no effect if count is not None.
    fields: None is default, get all fields. Or user could choose some of these fields.  
    Return : pandas.DataFrame
    '''
    security = convert_security(security)
    if security is None:
        return
    
    
    try:
        if count:
            assert isinstance(count, int), 'count 必须是int类型'
        else:
            count = 0
        dfcols = ['current','high','low','volume','money','position',
                                   'a1_p','a1_v','b1_p','b1_v','tradingday']
        if fields :
           assert isinstance(fields,list) and len(fields) > 0, "fields 必须为list类型，并且不能为空."
           dfcols = [f for f in fields if f in dfcols]
        cols = json.dumps(dfcols)
        start_date = convert_start_date(start_date, 2, overnight)
        if not start_date:
            return None
        end_date = convert_end_date(end_date, 2, overnight)
        if not end_date:
            return None

        return qedataClient.instance()('get_ticks',**locals())
    except Exception as e:
        print("get_tick Error:", e.__traceback__.tb_lineno,e)
        return None

@assert_auth
def get_securities_list(stype="all",dateWindow=None, exchange="all"):
    validTypes = ['all', 'options', 'futures', 'spot']
    if not stype in validTypes:
        print("stype不合法, 合法值如下： [\'all\', \'options\', \'futures\']")
        
        return None
    validExchanges =['DCE', 'SSE',"SFE","ZCE","INE","CCF","GFE","ALL"]
    exID = exchange.upper()
    if not exID in validExchanges:
        print("exchange不合法, 合法值如下:", validExchanges)
        return None 
    #print('dataWindow', dateWindow)
    try:
        if dateWindow:
            if len(dateWindow) == 2:
                if isinstance(dateWindow[0], datetime) or isinstance(dateWindow[0],date):
                    dateWindow[0] = dateWindow[0].strftime("%Y-%m-%d")
                if isinstance(dateWindow[1], datetime) or isinstance(dateWindow[1],date):
                    dateWindow[1] = dateWindow[1].strftime("%Y-%m-%d")
                curday = datetime.now().strftime("%Y-%m-%d")
                start_dt  = dateWindow[0] if dateWindow[0] != '' else curday
                end_dt = dateWindow[1] if dateWindow[1] != '' else curday
            else:
                print('dateWindow 格式应为 [start, end].')
                return None
            
            
            
            if not isinstance(dateWindow, list)  or not isinstance(start_dt, str) or  not isinstance(end_dt, str):
                print("不合法的dateWindow, 正确示例:  ['2021-10-11,'2021-12-31']表示日期在2021-10-11到2021-12-31日之间(2021-12-31 当天包含在内) 空字符串''代表今天.")
                return None
            if start_dt > end_dt:
                start_dt, end_dt = end_dt, start_dt
    except ValueError:
        print('dateWindow日期格式不对，应该为 %Y-%m-%d, 比如 \'2015-01-01\'')
        return None
    if dateWindow:
        dateWindow = json.dumps(dateWindow)
    else:
        dateWindow = json.dumps([])
    return qedataClient.instance()('get_securities_list',**locals())

@assert_auth
def get_prod_open_time(instid):
    instid = convert_security(instid)
    return qedataClient.instance()('get_prod_open_time',**locals())

def is_valid_date(dstr):
    try:
        datetime.strptime(dstr, '%Y-%m-%d')
        return True
    except:
        return False
    
@assert_auth
def get_dominant_instID(symbol, curdate=None, code='9999'):
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
    return qedataClient.instance()('get_dominant_instID', **locals())

@assert_auth
def get_dominant_instIDs(symbols, start_date, end_date, code='9999'):
    '''
    get dominant instrumentID for given symbol and date

    Parameters
    ----------
    symbols : TYPE list of String
        such as 'AG', the symbol of underlying product
    date : TYPE string
        such as '2021-10-10'

    Returns
    -------
    InstrumentID or '' if not found.

    '''    
    syms = []
    if isinstance(symbols, str):
        symbols = [symbols]
    if not isinstance(symbols,list) :
        print('symbols必须是合法合约的list')
        return None
    for sym in symbols:
        if not isinstance(sym, str):
            print('symbols必须是合法合约的list')
            return None
        else:
            syms.append(sym.upper())
    syms = json.dumps(syms)
    if isinstance(start_date, datetime) or isinstance(start_date, date):
        start_date = start_date.strftime('%Y-%m-%d')
    elif  isinstance(start_date, str):
        if len(start_date) != 10 or not is_valid_date(start_date):
            print('start_date不是合法的日期格式 正确格式比如"2020-08-02"')
            return None
    if isinstance(end_date, datetime) or isinstance(end_date, date):
        end_date = end_date.strftime('%Y-%m-%d')
    elif  isinstance(end_date, str):
        if len(end_date) != 10 or not is_valid_date(end_date):
            print('end_date不是合法的日期格式 正确格式比如"2020-08-02"')
            return None
    del symbols    
    return qedataClient.instance()('get_dominant_instIDs', **locals())

def readProd(instid):
    prod = instid[:2]
    if len(instid) < 2:
        return instid
    if prod[1].isdigit():
        prod = prod[:1]
    return prod

@assert_auth
def get_all_products():
    return qedataClient().instance()('get_all_products',**locals())

@assert_auth
def get_realtime_minute_prices(insts):
    if isinstance(insts, str):
        insts = [insts]
    if not isinstance(insts,list) :
        print('insts必须是合法合约的list')
        return None
    instids = json.dumps(insts)
    del insts
    return qedataClient.instance()('get_realtime_minute_prices', **locals())
    
@assert_auth
def get_instrument_setting(instid, exact_match=False):
    instid = convert_security(instid)
    prod = readProd(instid)
    if instid is None:
        return None
        
    elif instid[-3:] == 'SSE' :
        if len(instid) < 11: ## stocks and funds
        
            res ={'instid':instid, 'marglong':100.0,'margshort':100.0,
                  'openfeerate':4.87/10000,'closefeerate':0,'openfee':0,
                  'closefee':0, 'closetodayrate':1, 'refprice':0,
                  'volmult': 1, 'ticksize':0.001}
        else: ## option
            #longmarg = "presett+max(0.12*spreclose-max(strike-spreclose,0), 0.07*spreclose)"
            #shortmarg = "min(presett+max(0.12*spreclose-max(spreclose-strike,0), 0.07*strike), strike)"
            longmarg = 0
            shortmarg = 12
            res ={'instid':instid, 'marglong':longmarg,'margshort':shortmarg,
                  'openfeerate':0,'closefeerate':0,'openfee':1.3,
                  'closefee':0, 'closetodayrate':0, 'refprice':0,
                  'volmult': 10000, 'ticksize':0.0001}
        return res        
    elif instid[-3:] == 'SZE' :
        if len(instid) < 11: ## stocks and funds
        
            res ={'instid':instid, 'marglong':100.0,'margshort':100.0,
                  'openfeerate':4.87/10000,'closefeerate':0,'openfee':0,
                  'closefee':0, 'closetodayrate':1, 'refprice':0,
                  'volmult': 1, 'ticksize':0.001}
        else: ## option
            #longmarg = "presett+max(0.12*spreclose-max(strike-spreclose,0), 0.07*spreclose)"
            #shortmarg = "min(presett+max(0.12*spreclose-max(spreclose-strike,0), 0.07*strike), strike)"
            longmarg = 0
            shortmarg = 12
            res ={'instid':instid, 'marglong':longmarg,'margshort':shortmarg,
                  'openfeerate':0,'closefeerate':0,'openfee':0.45,
                  'closefee':0, 'closetodayrate':0, 'refprice':0,
                  'volmult': 10000, 'ticksize':0.0001}
        return res        
    elif prod in ["IO","MO"]:
        longmarg = "max(premium+spreclose*0.1-max(strike-spreclose,0),premium+spreclose*0.1*0.5)"
        shortmarg = "max(premium+spreclose*0.1-max(spreclose-strike,0),premium+spreclose*0.1*0.5)"
        res ={'instid':instid, 'marglong':longmarg,'margshort':shortmarg,
                  'openfeerate':0,'closefeerate':0,'openfee':15,
                  'closefee':0, 'closetodayrate':1.0, 'refprice':15,
                  'volmult': 100, 'ticksize':0.2}
        return res        
    else:
        return qedataClient.instance()('get_instrument_setting', **locals())
    

@assert_auth
def get_price(security, start_date, end_date, freq='minute', fields=None, overnight=False, silent=False):
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
        return qedataClient.instance()('get_price',**locals())
    except Exception as e:
        print("get_price Error:", e.__traceback__.tb_lineno,e)
        return None



@assert_auth
def get_bar_data(instids, tradingday, count=0, freq=1):
    try:
        assert isinstance(instids, list),'instids 必须是合约名list'
        #tnames = [inst2tablename(inst) for inst in instids]
        if isinstance(tradingday, str):
            tday = tradingday.replace('-','')
            if tday == '':
                tday = datetime.now().strftime('%Y%m%d')
        elif isinstance(tradingday, datetime) or isinstance(tradingday, date):
            tday = tradingday.strftime('%Ym%d')
        else:
            raise TypeError
        instids = json.dumps(instids)    
        lcount = count
        if freq != 1:
            count = 0
        data = qedataClient.instance()('get_bar_data', **locals())
       #print(data)
        if data:
                f=str(freq)+'min'
                for instid in data.keys():  
                    df=data[instid]
                    if len(df) > 0:
                        #print(df.time)
                        df['runtime']= pd.to_datetime(df.time, format='%Y%m%d%H%M%S',errors='ignore')
                        #for i in range(len(df['time'])):
                        #    df['runtime'].loc[i]=datetime.datetime.strptime(str(df['time'].loc[i]), "%Y%m%d%H%M%S")
                        df.set_index(["runtime"], inplace=True)
                        #print(df)
                        if f=='1min':
                            del data[instid]['time']
                        else:
                            df2 = pd.DataFrame(columns=df.columns)
                            #print('111',df2)
                            for col in df.columns:
                                tmp = pd.Series(index=df.index, data=df.loc[:,col])
                                if col == "open":
                                    tmp=df[col].resample(f, label='right', closed='right').first()
                                elif col =="close":
                                    tmp=df[col].resample(f, label='right', closed='right').last()
                                elif col == 'high':
                                    tmp=df[col].resample(f, label='right', closed='right').max()
                                elif col == 'low':
                                    tmp=df[col].resample(f, label='right', closed='right').min()
                                elif col == 'volume':
                                    tmp=df[col].resample(f, label='right', closed='right').sum()
                                elif col == 'money':
                                    tmp=df[col].resample(f, label='right', closed='right').sum()
                                elif col == 'position':
                                    tmp = df[col].resample(f, label='right', closed='right').last()
                                elif col == 'presett':
                                    tmp=df[col].resample(f, label='right', closed='right').last()
                                elif col == 'preclose':
                                    tmp=df[col].resample(f, label='right', closed='right').last()
                                elif col == 'lowerlimit':
                                    tmp=df[col].resample(f, label='right', closed='right').last()
                                elif col == 'upperlimit':
                                    tmp=df[col].resample(f, label='right', closed='right').last()
                                elif col == 'tradingday':
                                    tmp=df[col].resample(f, label='right', closed='right').last()
                                df2.loc[:,col] = tmp
                            #print(df2)
                            del df2['time']
                            if isinstance(lcount, int) and lcount > 0:
                                data[instid]=df2.dropna(how='any').iloc[-lcount:,]
                            else:
                                data[instid]=df2.dropna(how='any')
        return data
    except Exception as e:
        print("get_bar_data Error:", e.__traceback__.tb_lineno,e)
        return None

@assert_auth
def get_broker_info(broker):
    try:
        assert isinstance(broker, str),'broker需要是合法的期货公司代码字符串'
        return qedataClient.instance()('get_broker_info', **locals())

    except Exception as e:
        print("get_broker_info Error:", e.__traceback__.tb_lineno,e)
        return None

@assert_auth
def get_valid_instID(instid):
    try:
        assert isinstance(instid, str) and len(instid)>=5,'instid需要是合法的合约代码字符串'
        inst = instid
        prod = inst[:2]
        if prod[1].isdigit():
            prod = inst[:1]
        if instid.find('9999') >= 0:
            return get_dominant_instID(prod)
        elif instid.find('9998') >= 0:
            return get_dominant_instID(prod,code='9998')
        else:
            return qedataClient.instance()('get_valid_instID', **locals())

    except Exception as e:
        print("get_valid_instID Error:", e.__traceback__.tb_lineno,e)
        return None

@assert_auth
def is_valid_instID(instid):
    try:
        assert isinstance(instid, str) and len(instid)>=9,'instid需要是合法的合约代码字符串'
        instid = instid.upper()
        instid = instid.replace('.','_')
        instid = instid.replace('-','_')
        if instid.find('(T+D)') >= 0:
            instid.replace('(T+D)','_T_D')
        if instid in ['510300_SSE','510050_SSE']:
            return True
        elif instid in ['AG_T_D_SGE','AU_T_D_SGE','AU99_99_SGE','MAU_T_D_SGE']:
            return True
        else:
            return qedataClient.instance()('is_valid_instID', **locals())

    except Exception as e:
        print("is_valid_instID Error:", e.__traceback__.tb_lineno,e)
        return None

@assert_auth
def is_valid_trade_time(instid, curtime):
    try:
        assert isinstance(instid, str) and len(instid)>=9,'instid需要是合法的合约代码字符串'
        assert isinstance(curtime, datetime), 'curtime必须是datetime类型'
        weekday = curtime.weekday()
        timenum = curtime.hour * 100 + curtime.minute
        del curtime
        return qedataClient.instance()('is_valid_trade_time', **locals())

    except Exception as e:
        print("is_valid_trade_time Error:", e.__traceback__.tb_lineno,e)
        return None

@assert_auth
def get_product_spot_price(symbol, start_date, end_date):
    try:
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        elif isinstance(start_date, str):
            if len(start_date) != 10 or not is_valid_date(start_date):
                print('Invalid start_date')
                return None
        if isinstance(end_date, datetime) :
            end_date = end_date.strftime('%Y-%m-%d')
        elif isinstance(end_date, str):
            if len(end_date) != 10 or not is_valid_date(end_date):
                print('Invalid end_date')
                return None
        return qedataClient.instance()('get_product_spot_price', **locals())
    except Exception as e:
        print("get_product_spot_price Error:", e.__traceback__.tb_lineno,e)
        return None

@assert_auth
def get_product_invent_orders(symbol, start_date, end_date):
    try:
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        elif isinstance(start_date, str):
            if len(start_date) != 10 or not is_valid_date(start_date):
                print('Invalid start_date')
                return None
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d')
        elif isinstance(end_date, str):
            if len(end_date) != 10 or not is_valid_date(end_date):
                print('Invalid end_date')
                return None
        return qedataClient.instance()('get_product_invent_orders', **locals())
    except Exception as e:
        print("get_product_invent_orders Error:", e.__traceback__.tb_lineno,e)
        return None



#########################algo trades#####################################
@assert_auth
def get_package_address(plugin, plat, version, macaddr):
        return qedataClient.instance()('get_package_address', **locals())

@assert_auth
def get_plugin_permission(plugin, plat, version, macaddr, key, signval):
        return qedataClient.instance()('get_plugin_permission', **locals())
        
##############################stratmarket############################
def sm_get_clone_strat_list():
    try:
        #print('get_clone_strat_list')
        if not qedataClient.check_login():
            print('您需要先用login函数登录策略超市')
            return None
        else:
            #print('enter api')
            return qedataClient.instance()('sm_get_clone_strat_list', **locals())
    
    except Exception as e:
        print("get_clone_strat_list Error:", e.__traceback__.tb_lineno,e)

def sm_get_clone_strat_position(strats:list):
    try:
        assert isinstance(strats,list), 'strats必须是策略名列表'
        strats = json.dumps(strats)
        if not qedataClient.check_login():
            print('您需要先用login函数登录策略超市')
            return None
        else:
            return qedataClient.instance()('sm_get_clone_strat_position', **locals())
    
    except Exception as e:
        print("get_clone_strat_position Error:", e.__traceback__.tb_lineno,e)
    
@assert_auth
def get_instrument_broker_ranking(instid, curdate, rankname):
    valid_rankname = ['tradevol',
                      'longpos',
                      'longpos_add',
                      'longpos_reduce',
                      'longpos_net',
                      'shortpos',
                      'shortpos_add',
                      'shortpos_reduce',
                      'shortpos_net']
    if not rankname in valid_rankname:
        print(f'不合法的rankname:{rankname}, rankname可以是{valid_rankname}')
        return None
    insts = instid.split('.')
    instID = insts[0].upper()

    if isinstance(curdate, datetime) or isinstance(curdate, date):
        curdate = curdate.strftime('%Y-%m-%d')
    elif isinstance(curdate, str):
        if len(curdate) != 10 or not is_valid_date(curdate):
            print('Invalid curdate')
            return None
    del insts
    return qedataClient.instance()('get_instrument_broker_ranking', **locals())
    
@assert_auth
def get_instrument_broker_holding(broker, instid, start_date, end_date):
    insts = instid.split('.')
    instID = insts[0].upper()

    if isinstance(start_date, datetime) or isinstance(start_date, date):
        start_date = start_date.strftime('%Y-%m-%d')
    elif isinstance(start_date, str):
        if len(start_date) != 10 or not is_valid_date(start_date):
            print('Invalid start_date')
            return None
    if isinstance(end_date, datetime) or isinstance(end_date, date):
        end_date = end_date.strftime('%Y-%m-%d')
    elif isinstance(end_date, str):
        if len(end_date) != 10 or not is_valid_date(end_date):
            print('Invalid end_date')
            return None
    del insts        
    return qedataClient.instance()('get_instrument_broker_holding', **locals())
    
@assert_auth
def get_instrument_broker_pnl(broker, instid, start_date, end_date):
    insts = instid.split('.')
    instID = insts[0].upper()

    if isinstance(start_date, datetime) or isinstance(start_date, date):
        start_date = start_date.strftime('%Y-%m-%d')
    elif isinstance(start_date, str):
        if len(start_date) != 10 or not is_valid_date(start_date):
            print('Invalid start_date')
            return None
    if isinstance(end_date, datetime) or isinstance(end_date, date):
        end_date = end_date.strftime('%Y-%m-%d')
    elif isinstance(end_date, str):
        if len(end_date) != 10 or not is_valid_date(end_date):
            print('Invalid end_date')
            return None
    del insts        
    return qedataClient.instance()('get_instrument_broker_pnl', **locals())

@assert_auth
def update_public_ip(hostip):
    return qedataClient.instance()('update_public_ip', **locals())


@assert_auth
def get_risk_control_parameter():
    return qedataClient.instance()('get_risk_control_parameter', **locals())


__all__ = []

def _collect_func():
    funcs = []
    for func in globals().keys():
        if func.startswith("get") or func.startswith("sm_get") or func.startswith("is_") or func.startswith("update_"):
            funcs.append(func)
    return funcs

__all__.extend(_collect_func())
#print(__all__)
del _collect_func