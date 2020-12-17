import numpy as np
import time
from scipy import interpolate


def k_type_fit():
    volt = []
    with open("k-type-table.txt", "r") as f:
        lines = f.readlines()
    for l in lines:
        l = l.strip().split('\t')
        volt += [(float(v)/1000) for v in l[1:-1:1]]
    temp = np.arange(volt.__len__())
    f = interpolate.interp1d(volt, temp, bounds_error=False, fill_value="extrapolate")
    return f

def k_type_fit_inverse():
    volt = []
    with open("k-type-table.txt", "r") as f:
        lines = f.readlines()
    for l in lines:
        l = l.strip().split('\t')
        volt += [(float(v)/1000)  for v in l[1:-1:1]]
    temp = np.arange(volt.__len__())
    f = interpolate.interp1d(temp, volt, bounds_error=False, fill_value="extrapolate")
    return f

if __name__ == "__main__":
    f = k_type_fit()
    t0 = time.time()
    print(f([10.153/1000]))
    print(time.time() - t0)
