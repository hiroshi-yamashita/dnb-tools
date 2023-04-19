# Spatial harvested_population model
# van Nes, Egbert H., and Marten Scheffer. "Implications of spatial heterogeneity for catastrophic regime shifts in ecosystems." Ecology 86.7 (2005): 1797-1807.
import numpy as np
import matplotlib.pyplot as plt
import tqdm


def f(x, c):
    K = 10
    return x*(1 - x/K) - c * (x**2)/(1 + x**2)


def ddx(X, dx):
    return dx*(np.roll(X, 1, axis=0) + np.roll(X, 1, axis=1) + np.roll(X, -1, axis=0) + np.roll(X, -1, axis=1) - 4 * X)


def get_data(n=20, sigma=0.1, seed=0):
    np.random.seed(seed)

    dt = 0.1
    dx = 0.01
    T = 1000
    times = np.arange(0, T, dt)

    x = np.zeros((times.shape[0], n, n))
    omega = sigma * np.random.randn(times.shape[0], n, n)

    p_min = 1
    p_max = 2.8
    c = p_min + (p_max - p_min) * times/T
    x0 = 8.0*np.ones((n, n))
    for k in range((times.shape[0]-1)//10):
        x0 = x0 + dt * (f(x0, c[0]) + ddx(x[k], dx))
        x0[x0 < 0] = 0

    x[0] = x0
    print('Generating time-series data of a harvested_population model')
    for k in tqdm.tqdm(range(times.shape[0]-1)):
        x[k+1] = x[k] + dt * (f(x[k], c[k]) + ddx(x[k], dx)
                              ) + np.sqrt(dt)*omega[k]
        x[k+1, x[k+1] < 0] = 0

    y = np.zeros(times.shape[0])
    y[c > 2.604] = 1
    return times, x.reshape(-1, n*n), y


def overview():
    times, x, y = get_data(n=20, sigma=0.1)
    x = x.reshape(-1, 20, 20)
    tau1 = 1000
    tau2 = np.argmax(y)
    tau3 = -500

    plt.figure(figsize=(20, 10))

    plt.subplot2grid((2, 3), (0, 1))
    plt.grid(False)
    xtmp = x[tau2] - x[tau2].mean()
    # x_delta = xtmp.max()-xtmp.min()
    x_delta = 4*xtmp.std()
    plt.title(f'$t$ = {times[tau2]:.1f}')
    plt.imshow(xtmp, cmap="GnBu")
    plt.clim([xtmp.mean() - x_delta/2, xtmp.mean() + x_delta/2])

    plt.subplot2grid((2, 3), (0, 0))
    plt.grid(False)
    xtmp = x[tau1] - x[tau1].mean()
    plt.title(f'$t$ = {times[tau1]:.1f}')
    plt.imshow(xtmp, cmap="GnBu")
    plt.clim([xtmp.mean() - x_delta/2, xtmp.mean() + x_delta/2])

    tmp = plt.subplot2grid((2, 3), (0, 2))
    plt.grid(False)
    xtmp = x[tau3] - x[tau3].mean()
    plt.title(f'$t$ = {times[tau3]:.1f}')
    plt.imshow(xtmp, cmap="GnBu")
    plt.clim([xtmp.mean() - x_delta/2, xtmp.mean() + x_delta/2])
    plt.colorbar()
    plt.text(18, -1, '$E[x(t)]$ + ')

    plt.subplot2grid((2, 3), (1, 0), colspan=3)
    plt.plot(times, x.reshape(-1, 400)[:, :50], zorder=1)
    plt.scatter(times[tau1], x.mean((1, 2))[tau1],
                s=200, color='red', zorder=2)
    plt.scatter(times[tau2], x.mean((1, 2))[tau2],
                s=200, color='red', zorder=2)
    plt.scatter(times[tau3], x.mean((1, 2))[tau3],
                s=200, color='red', zorder=2)

    plt.text(times[tau1], x.mean((1, 2))[tau1], f'$t$ = {times[tau1]:.1f}')
    plt.text(times[tau2], x.mean((1, 2))[tau2], f'$t$ = {times[tau2]:.1f}')
    plt.text(times[tau3], x.mean((1, 2))[tau3], f'$t$ = {times[tau3]:.1f}')
    plt.xlim([times[0], times[-1]])
    plt.xlabel('Time : $t$')
    plt.ylabel('Biomass : $x_i$')
