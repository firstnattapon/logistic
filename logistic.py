import numpy as np
import matplotlib.pyplot as plt

λ = 3.782
N = 50 
x = np.zeros(N)
x[0] = 0.779
for n in range(N-1):
    x[n+1] = λ*x[n]*(1-x[n])
    
    
 
st.line_chart(x)
