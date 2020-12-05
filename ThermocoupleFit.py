import numpy as np
import time
from scipy import interpolate


def k_type_fit():
    gain = 63.2
    offset = 5
    volt = []
    with open("k-type-table.txt", "r") as f:
        lines = f.readlines()
    for l in lines:
        l = l.strip().split('\t')
        volt += [(float(v0) * gain ) / 1000 / 3.3 * 2 ** 12 for v in l[1:-1:1]]
    temp = np.arange(volt.__len__())
    f = interpolate.interp1d(volt, temp, bounds_error=False, fill_value="extrapolate")
    return f


if __name__ == "__main__":
    f = k_type_fit()
    t0 = time.time()
    print(f([30, 40, 50]))
    print(time.time() - t0)
