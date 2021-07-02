import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pandas_datareader  as pdr
import ccxt
import warnings
from datetime import datetime

class  delta :
    def __init__(self , usd = 1000 , fix_value = 0.50, pair_data = 'SRM-PERP', timeframe = '5m' 
                 , limit  = 2016 , series_num = [None] , minimum_re = 0.005):
        self.usd    = usd
        self.fix_value  = fix_value
        self.pair_data = pair_data
        self.timeframe = timeframe
        self.limit = limit
        self.series_num = series_num
        self.minimum_re = minimum_re
        
    def get_data(self):
        exchange = ccxt.ftx({'apiKey': '', 'secret': '', 'enableRateLimit': True})
        ohlcv = exchange.fetch_ohlcv(self.pair_data, self.timeframe, limit=self.limit)
        ohlcv = exchange.convert_ohlcv_to_trading_view(ohlcv)
        df = pd.DataFrame(ohlcv)
        df.t = df.t.apply(lambda x: datetime.fromtimestamp(x))
        df = df.set_index(df['t']);
        df = df.drop(['t'], axis=1)
        df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
        df = df.drop(['open', 'high' , 'low' , 'volume'] , axis=1) 
        df = df.dropna()
        return df
    
    def series(self):
        series  = self.get_data()
        series['index'] = [ i for i in range(len(series))]
        series['perdit'] =series['index'].apply(func= (lambda x : np.where( x in self.series_num , 1 , 0)))
        return series
    
    def  nav (self):
        nav_data = self.series()
        nav_data['amount'] =  np.nan
        for i in range(len(nav_data)): # amount
            if i == 0 :
                nav_data.iloc[i, 3] =   (self.usd * self.fix_value)  / nav_data.iloc[i, 0]
            else :
                nav_data.iloc[i, 3] =   np.where(nav_data.iloc[i, 2] == 0 ,  nav_data.iloc[i-1, 3] , 
                                                (self.usd * self.fix_value) / nav_data.iloc[i, 0])          
                
        nav_data['asset_value'] =  (nav_data['close']*nav_data['amount']) 

        nav_data['re'] =  np.nan
        for i in range(len(nav_data)): # re
            if i == 0 :
                nav_data.iloc[i, 5] =    0
            else :
                nav_data.iloc[i, 5] =    np.where(nav_data.iloc[i, 2] == 1 and 
                                                  (abs((nav_data.iloc[i-1, 3] * nav_data.iloc[i, 0]) - (self.usd * self.fix_value)) 
                                                  / (self.usd * self.fix_value)) >= self.minimum_re
                                                  , (nav_data.iloc[i-1, 3] * nav_data.iloc[i, 0]) -  (self.usd * self.fix_value) , 0)

        nav_data['cash'] =  np.nan
        for i in range(len(nav_data)): # cash
            if i == 0 :
                nav_data.iloc[i, 6] =    (self.usd * self.fix_value)
            else :
                nav_data.iloc[i, 6] =   (nav_data.iloc[i-1, 6] + nav_data.iloc[i, 5] )

        nav_data['sumusd'] =  (nav_data['cash'] + nav_data['asset_value'])

        return nav_data

    def  mkt (self):
        mkt_data  = self.nav()
        mkt_data[':'] = ':'
        mkt_data['cash_mkt'] =  (self.usd * self.fix_value)
        mkt_data['amount_mkt'] =   (mkt_data.iloc[0, 9]  / mkt_data.iloc[0, 0])
        mkt_data['assetvalue_mkt'] =  mkt_data['close'] * mkt_data['amount_mkt']
        mkt_data['sumusd_mkt'] = (mkt_data['assetvalue_mkt']  + mkt_data['cash_mkt'])

        return mkt_data

    def cf (self):
        cf_data = self.mkt()
        cf_data[': '] = ': '
        cf_data['cf_usd'] =   cf_data['sumusd']  - cf_data['sumusd_mkt']
        cf_data['cf_change'] =  (cf_data['cf_usd'] /  cf_data.iloc[0 , 7]) * 100

        return cf_data

    def change (self):
        change_data = self.cf()
        change_data[' : '] = ' : '
        change_data['price_change'] =   ((change_data['sumusd_mkt'] - change_data.iloc[0, 12]) / change_data.iloc[0, 12]) * 100
        change_data['pv_change']  = ((change_data['sumusd'] - change_data.iloc[0 , 7] ) / change_data.iloc[0 , 7]) *100
        change_data['0'] = 0
        return change_data
    
λ = st.sidebar.slider('λ', min_value=0.0 , max_value=4.0 , value=0.95 , step= 0.01)
N = st.sidebar.slider('N', min_value=50 , max_value=100 , value=50 , step= 0.01) 
x = np.zeros(N)
x[0] = st.sidebar.slider('x0', min_value=0.0, max_value=1.0, value=0.50 , step= 0.01)
for n in range(N-1):
    x[n+1] = λ*x[n]*(1-x[n])

max = st.sidebar.number_input('max' , 2016)
x = np.around(x*max)
    
fig = go.Figure(data=go.Scatter(y=x , mode='lines+markers'))
st.plotly_chart(fig)

fig = px.scatter(x=x ,y=x)
for l in np.sort(np.unique(x)): fig.add_hline(y=l , line_width=1.0)
st.plotly_chart(fig)

if st.sidebar.checkbox('linear',value=False) :
    code = [ i for i in range(max)]
else :
    code = np.sort(np.unique(x))
    
st.code('{} \n\n n = {}'.format(code , len(code)))

#  ____________________________________________________________________

col1, col2 , col3 , col4 , col5 , col6   = st.beta_columns(6)
pair_data = col1.text_input("pair_data", "CRV/USD")
fix_value = float(col2.text_input("fix_value", "0.5" ))
invest =  int(col3.text_input("invest" , "1000"))
timeframe = col4.text_input("timeframe", "5m")
limit =  int(col5.text_input("limit" , "2016"))
minimum_re = float(col6.text_input("minimum_re" , "0.005"))

delta_A = delta(usd = invest ,
                fix_value = fix_value ,  
                pair_data = pair_data ,
                timeframe =  timeframe  ,
                limit  = limit ,
                series_num = code ,
                minimum_re = minimum_re)
      
delta_A= delta_A.change()

_ = delta_A[['cf_change' ,'price_change' ,'0' ]] ; _.columns = ['1: cf_%', '2: mkt_%' , "3: zero_line"] 
st.line_chart(_)
_ = delta_A[[ 'pv_change', 'price_change' , '0' ]] ; _.columns = ['1: pv_%', '2: mkt_%' , "3: zero_line"]
st.line_chart(_)

st.write('data        :' , len(delta_A) )
st.write('')
st.write( 'cf_usd      :'    ,  round(float(delta_A['cf_usd'][-1]) , 2 ) ,'$')
st.write('')
st.write( 'cf_change :'  , round(delta_A['cf_change'][-1] , 2),'%')

# _, _ , head , _ ,   = st.beta_columns(4) 
# head.write('เริ่ม')
# st.dataframe(delta_A.head(1))
# _, _ , tail , _ ,   = st.beta_columns(4)
# tail.write('ล่าสุด')
# st.dataframe(delta_A.tail(1))

st.dataframe(delta_A)

