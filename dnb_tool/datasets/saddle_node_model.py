import numpy as np
import tqdm


def f(x, p):
    return x - 1/3 * (x**3) + p


def get_data(sigma=0.01, seed=0):
    np.random.seed(seed)

    T = 1000
    dt = 0.01
    times = np.arange(0, T, dt)

    omega = sigma * np.random.randn(times.shape[0])

    p = 2/3 - 0.09 + 0.1 * times.reshape(-1)/T
    x0 = - 1
    # search initial equilibrium point
    for t in range(times.shape[0]//10):
        x0 = x0 + dt * (f(x0, p[0]))

    x = np.zeros((times.shape[0]))
    x[0] = x0

    print('Generating time-series data of a simple saddle node model.')
    for t in tqdm.tqdm(range(times.shape[0] - 1)):
        x[t+1] = x[t] + dt * (f(x[t], p[t])) + np.sqrt(dt)*omega[t]

    y = np.zeros(x.shape[:2])
    y[p > 2/3] = 1
    return times, x, y
