import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

λ = st.sidebar.number_input('λ',3.0)
N = st.sidebar.slider('N', min_value=50 , max_value=100) 
x = np.zeros(N)
x[0] = st.sidebar.slider('x0', min_value=0.0, max_value=1.0)
for n in range(N-1):
    x[n+1] = λ*x[n]*(1-x[n])

max = st.sidebar.number_input('max' , 2016)
x = np.around(x*max)
    
fig = go.Figure(data=go.Scatter(y=x , mode='lines+markers'))
st.plotly_chart(fig)

fig = px.scatter(x=x ,y=x)
for l in x: fig.add_hline(y=l , line_width=1.0)
st.plotly_chart(fig)

code = np.sort(np.unique(x))
st.code('{} \n\n n = {}'.format(code , len(code)))

