import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pandas_datareader  as pdr
import ccxt
import warnings
import datetime

class  delta :
    def __init__(self , usd = 1000 , fix_value = 0.50, pair_data = 'SRM-PERP', timeframe = '5m' 
                 , limit  = 5000 , series_num = [None] , minimum_re = 0.005 , start_end = [170 , 177]):
        self.usd    = usd
        self.fix_value  = fix_value
        self.pair_data = pair_data
        self.timeframe = timeframe
        self.limit = limit
        self.series_num = series_num
        self.minimum_re = minimum_re
        self.start_end = start_end
        
    @st.cache(suppress_st_warning=True)
    def get_data(self):
        exchange = ccxt.ftx({'apiKey': '', 'secret': '', 'enableRateLimit': True})
        ohlcv = exchange.fetch_ohlcv(self.pair_data, self.timeframe, limit=self.limit)
        ohlcv = exchange.convert_ohlcv_to_trading_view(ohlcv)
        df = pd.DataFrame(ohlcv)
        df.t = df.t.apply(lambda x: datetime.datetime.fromtimestamp(x))
        df = df.set_index(df['t']);
        df.t = df.index.dayofyear
        df = df.loc[df.t >= self.start_end[0]]
        df = df.loc[df.t <= self.start_end[1]]
        df = df.drop(['t'], axis=1)
        df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
        df = df.drop(['open', 'high' , 'low' , 'volume'] , axis=1) 
        df = df.dropna()
        return df

    def series(self):
        series  = self.get_data()
        series['index'] =np.array([ i for i in range(len(series))])
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

        return change_data

    def  final (self):
        final = self.change()
        final[' :  '] = ' :  '
        final['0'] =  0
        final['t'] =    final.index.dayofyear
        return final
    

exchange = ccxt.ftx({'apiKey': '', 'secret': '', 'enableRateLimit': True})
e = exchange.load_markets()
pair_x   = [i for i in e if i[-1] == 'P']
pair_x   = [i for i in pair_x if i[-9:] != 'BULL/USDT']
pair_x   = [i for i in pair_x if i[-9:] != 'BEAR/USDT']
pair_x   = [i for i in pair_x if i[-9:] != 'DOWN/USDT']
pair_x   = [i for i in pair_x if i[-7:] != 'UP/USDT']    
    
    
linear =  st.sidebar.checkbox('linear',value=False)    
Scatter =  st.sidebar.checkbox('Scatter',value=False)    
cf =  st.sidebar.checkbox('cf',value=False)    
pair_data = st.sidebar.selectbox('pair_data', pair_x)

start = st.sidebar.date_input('start' , datetime.date(2021,6,21)) ; start = start.timetuple().tm_yday #; st.sidebar.write(start)
end = st.sidebar.date_input('end', datetime.date(2021,6,28)) ; end =  end.timetuple().tm_yday #; st.sidebar.write(end)
max = st.sidebar.number_input('max' ,0 , 5000 ,2304)

λ = st.sidebar.number_input('λ', min_value=0.0 , max_value=4.0 , value=4.00)
N = st.sidebar.number_input('N', min_value=50 , max_value=10000 , value=9999) 
x = np.zeros(N)
x[0] = st.sidebar.number_input('x0', min_value=0.001, max_value=0.999, value=0.042 , format="%.3f")

col2 , col3 , col4 , col5 , col6   = st.beta_columns(5)
fix_value = float(col2.text_input("fix_value", "0.5" ))
invest =  int(col3.text_input("invest" , "1000"))
timeframe = col4.text_input("timeframe", "5m")
limit =  int(col5.text_input("limit" , "5000"))
minimum_re = float(col6.text_input("minimum_re" , "0.005"))


button = st.sidebar.button('RUN_series')
if (button==True):
    for n in range(N-1):
        x[n+1] = λ*x[n]*(1-x[n])
        
    z = np.around(x*max)

    if linear:
        code = [ i for i in range(max)]
    else :
        code = np.sort(np.unique(z))
        
    if Scatter :    
        fig = go.Figure(data=go.Scatter(y= z , mode='lines+markers'))
        st.plotly_chart(fig)

        fig = px.scatter(x=z , y=z)
        for l in np.sort(np.unique(z)): fig.add_hline(y=l , line_width=1.0)
        st.plotly_chart(fig)
    else : pass            

    delta_A = delta(usd = invest ,
                    fix_value = fix_value ,  
                    pair_data = pair_data ,
                    timeframe =  timeframe  ,
                    limit  = limit ,
                    series_num = code  ,
                    minimum_re = minimum_re,
                    start_end = [start , end]
                   )
    delta_A= delta_A.final()        
    st.code('{} \n\n n = {}'.format(list(code) , len(code)))
    
    if cf :    
        _ = delta_A[['cf_change' ,'price_change' ,'0' ]] ; _.columns = ['1: cf_%', '2: mkt_%' , "3: zero_line"] 
        st.line_chart(_)
        _ = delta_A[[ 'pv_change', 'price_change' , '0' ]] ; _.columns = ['1: pv_%', '2: mkt_%' , "3: zero_line"]
        st.line_chart(_)
    else : pass
    
    st.sidebar.write('data        :' , len(delta_A) )
    st.sidebar.write('')
    st.sidebar.write( 'cf_usd      :'    ,  round(float(delta_A['cf_usd'][-1]) , 2 ) ,'$')
    st.sidebar.write('')
    st.sidebar.write( 'cf_change :'  , round(delta_A['cf_change'][-1] , 2),'%')

    st.stop()
else : pass


# st.dataframe(delta_A)
