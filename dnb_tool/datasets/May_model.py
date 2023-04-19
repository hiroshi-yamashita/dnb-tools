# Single harvested_population model
# May, Robert M. "Thresholds and breakpoints in ecosystems with a multiplicity of stable states." Nature 269.5628 (1977): 471-477.
import numpy as np
import matplotlib.pyplot as plt
import tqdm


def f(x, p):
    K = 10
    return x*(1 - x/K) - p*(x**2)/(x**2 + 1)


def get_data(sigma=0.01, seed=0):
    np.random.seed(seed)
    T = 1000
    dt = 0.01
    times = np.arange(0, T, dt)

    omega = sigma * np.random.randn(times.shape[0])

    p = 1.0 + 1.7 * times.reshape(-1)/T
    x0 = 2.0
    # search initial equilibrium point
    for t in range(times.shape[0]//10):
        x0 = x0 + dt * (f(x0, p[0]))
        if x0 < 0:
            x0 = 0

    x = np.zeros((times.shape[0]))
    x[0] = x0
    print('Generating time-series data of the May model')
    for t in tqdm.tqdm(range(times.shape[0] - 1)):
        x[t+1] = x[t] + dt * (f(x[t], p[t])) + np.sqrt(dt)*omega[t]
        if x[t+1] < 0:
            x[t+1] = 0

    y = np.zeros(x.shape[:2])
    y[p > 2.604] = 1
    return times, x, y
