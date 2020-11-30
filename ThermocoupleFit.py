import numpy as np
import time
from scipy import interpolate

def k_tpye_fit():
    temp = []
    volt = []
    with open("k-type-table.txt","r") as f:
        lines = f.readlines()
    for l in lines:
        l = l.strip().split('\t')
        volt += [float(t)/3.3*2**12/1000 for t in l[1:-1:1]]
    temp = np.arange(volt.__len__())
    f = interpolate.interp1d(volt,temp,bounds_error=False,fill_value="extrapolate")
    return f

if __name__ == "__main__":
    f = k_tpye_fit()
    t0 = time.time()
    print(f([30,40,50]))
    print(time.time()-t0)