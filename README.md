

## Project Description

- Provide history market quotation of futures and options in Chinese market for inquiry.
- Output pandas.DataFrame format data which is easy to use.
-  Support three frequency data: 'daily'/'mintue'/'tick'



## Installation

```
pip install qesdk
```



## Upgrade

```
pip install -U qesdk 
```



## Quick Start



#### Daily frequency

```
from qesdk.qedata import *
get_price('ZN2210.SFE','2022-07-11', '2022-07-24','daily')
```

return:

```
               open    close     high      low  volume         money  \
time                                                                   
2022-07-11  22890.0  22730.0  23095.0  22710.0    6622  7.586028e+08   
2022-07-12  22875.0  22825.0  23265.0  22570.0    6976  7.926840e+08   
2022-07-13  22825.0  22015.0  22830.0  21885.0    9616  1.090028e+09   
2022-07-14  21900.0  21385.0  22035.0  21175.0   17883  1.935010e+09   
2022-07-15  21400.0  21050.0  21505.0  20980.0   11737  1.242712e+09   
2022-07-18  21300.0  21780.0  21870.0  21215.0   10991  1.180527e+09   
2022-07-19  22120.0  22095.0  22230.0  22060.0    9348  1.035372e+09   
2022-07-20  21750.0  21970.0  22005.0  21600.0    8816  9.613756e+08   
2022-07-21  22300.0  22000.0  22300.0  21855.0    8543  9.477114e+08   
2022-07-22  21900.0  21925.0  21965.0  21770.0   13236  1.446647e+09   

            position  upperlimit  lowerlimit  presett  preclose   settle  
time                                                                      
2022-07-11   23345.0     25730.0     20215.0  22975.0   22890.0  22870.0  
2022-07-12   24395.0     25610.0     20125.0  22870.0   22950.0  22885.0  
2022-07-13   27160.0     25630.0     20135.0  22885.0   22825.0  22430.0  
2022-07-14   26170.0     25120.0     19735.0  22430.0   22015.0  21600.0  
2022-07-15   27301.0     24190.0     19005.0  21600.0   21385.0  21220.0  
2022-07-18   27857.0     23765.0     18670.0  21220.0   21050.0  21760.0  
2022-07-19   29230.0     24370.0     19145.0  21760.0   21985.0  21915.0  
2022-07-20   30704.0     24540.0     19285.0  21915.0   21660.0  21960.0  
2022-07-21   35460.0     24595.0     19320.0  21960.0   22095.0  22065.0  
2022-07-22   37524.0     24710.0     19415.0  22065.0   22000.0  21965.0  
```



#### Minute frequency

```
from qesdk.qedata import *
get_price('ZN2210.SFE','2022-07-11', '2022-07-24','minute')
```

return:

```
                        open    close     high      low  volume       money
time                                                                       
2022-07-11 09:01:00  22785.0  22760.0  22785.0  22700.0     163  18534950.0
2022-07-11 09:02:00  22760.0  22725.0  22760.0  22685.0     195  22134500.0
2022-07-11 09:03:00  22715.0  22720.0  22725.0  22700.0      39   4427900.0
2022-07-11 09:04:00  22720.0  22710.0  22720.0  22680.0      63   7152150.0
2022-07-11 09:05:00  22710.0  22700.0  22725.0  22690.0      47   5335800.0
...                      ...      ...      ...      ...     ...         ...
2022-07-23 00:56:00  22375.0  22360.0  22375.0  22360.0      13   1453650.0
2022-07-23 00:57:00  22375.0  22365.0  22375.0  22355.0      29   3242625.0
2022-07-23 00:58:00  22360.0  22355.0  22365.0  22355.0      25   2794725.0
2022-07-23 00:59:00  22355.0  22380.0  22385.0  22355.0      13   1454125.0
2022-07-23 01:00:00  22380.0  22400.0  22400.0  22375.0      69   7723875.0

[4170 rows x 6 columns]
```



#### Tick frequecy

```
from qesdk.qedata import *
get_ticks('ZN2210.SFE','2022-08-21', '2022-08-24',fields=['current', 'position','volume'])
```

return:

```
                         current  position  volume
time                                              
2022-08-22 09:00:00.500  24720.0   92068.0   61019
2022-08-22 09:00:01.000  24725.0   92054.0   61044
2022-08-22 09:00:01.500  24735.0   92052.0   61063
2022-08-22 09:00:02.000  24745.0   92071.0   61111
2022-08-22 09:00:02.500  24745.0   92067.0   61142
...                          ...       ...     ...
2022-08-23 23:59:54.000  24920.0   97685.0   42997
2022-08-23 23:59:54.500  24920.0   97685.0   42997
2022-08-23 23:59:55.500  24920.0   97685.0   42997
2022-08-23 23:59:59.500  24920.0   97685.0   42997
2022-08-24 00:00:00.000  24920.0   97685.0   42997

[8314 rows x 3 columns]
```



## More details

The detail document could be obtained on https://quantease.cn/newdoc
