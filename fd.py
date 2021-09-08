import numpy
import yfinance as yf
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import probplot

class dates():
    def __init__(self,fec=None,form='%d/%m/%Y'):
        if fec is None:
            fec=dt.date.today()
        if type(fec) == str:
            try:
                self.value=dt.datetime.strptime(fec,form)
            except:
                self.value=dt.datetime.strptime(fec,'%d/%m/%y')
            self.value=self.value.date()
        elif type(fec) is dt.datetime:
            self.value=fec.date()
        elif type(fec) is dt.date:
            self.value=fec
        elif type(fec)==pd._libs.tslibs.timestamps.Timestamp:
            self.value=fec.to_pydatetime().date()
        elif type(fec)==dates:
            self.value=fec.value
        else:
            raise Exception("Error in date format")
    def str(self,form='%d/%m/%Y'):
        return dt.datetime.strftime(self.value,form)
    def mod(self,q,period="d",save=False,eom=False,som=False):
        if period=="d":
            f=self.value+relativedelta(days=q)
        elif period=="m":
            f=self.value+relativedelta(months=q)
        elif period=="y":
            f=self.value+relativedelta(years=q)
        if eom:
            f=dt.datetime(f.year,f.month,monthrange(f.year,f.month)[1]).date()
        if som:
            f=dt.datetime(f.year,f.month,1).date()
        if save:
            self.value=f
            return self
        else:
            t=dates()
            t.value=f
            return t
    def dts(self):
        return f"dateserial({self.value.year},{self.value.month},{self.value.day})"
    def dts_or(self):
        return f"TO_DATE('{self.str()}', 'DD-MM-YYYY')"
class finance_data():
    def __init__(self):
        self.data  = pd.DataFrame()
    def _get_info(self,*args,**kwargs):
        self.data = yf.download(*args,**kwargs)
        if len(args[0])==1:
            self.data.columns = pd.MultiIndex.from_product([self.data.columns,args[0]])
        self.data.dropna(axis=0,how='all',inplace=True)
        self.data.fillna(method='ffill',inplace=True)
        self.data.fillna(method='bfill',inplace=True)

        #Columns for returns added
        print()
        for ticker in args[0]:
            print(ticker)
            self.data['Previous Close',ticker] = self.data['Adj Close',ticker].shift(1)
            self.data['Return',ticker] = self.data['Adj Close',ticker]/self.data['Previous Close',ticker]-1
            self.data['Log_return',ticker] = np.log(self.data['Return',ticker]+1)
        return self.data
x = finance_data()
x._get_info(['AAPL','GOOG','IBM','ABNB'],start='2010-01-31',end='2021-06-30')
x.data.loc['2020-01-31',('Adj Close','GOOG')]
x.data.xs('GOOG',level=1,axis=1)['Adj Close']
x.data['Return','AAPL'].plot()
x.data['Return','AAPL'].hist(bins=100)

##QQ Plot
probplot(x.data['Return','AAPL'].dropna(),dist='norm',fit=True,plot=plt)
print()

##With stats models
import statsmodels.api as sm
sm.qqplot(x.data['Return','AAPL'].dropna(),line='s')
