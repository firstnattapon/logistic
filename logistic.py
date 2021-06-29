import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

λ = 3.782
N = 50 
x = np.zeros(N)
x[0] = 0.779
for n in range(N-1):
    x[n+1] = λ*x[n]*(1-x[n])
    
    
 
# plt.plot(x , 's-')

# fig, ax = plt.subplots()
# ax.plot(x , 's-')
st.bar_chart(x)

# st.pyplot(fig)
