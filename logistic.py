import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go

λ = st.slider('λ', min_value=0.0, max_value=4.0 , 1.200 )


# λ = 3.782
N = 50 
x = np.zeros(N)
x[0] = 0.779
for n in range(N-1):
    x[n+1] = λ*x[n]*(1-x[n])
    
    
fig = go.Figure(data=go.Scatter(y=x , mode='lines+markers'))
st.plotly_chart(fig)
