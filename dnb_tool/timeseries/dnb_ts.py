import numpy as np
import time
import tqdm
from sklearn.decomposition import PCA
import ruptures as rpt


from numpy.lib.stride_tricks import sliding_window_view as sliding_window


def timer(func):
    def wrapper(*args, **kwargs):
        time_s = time.time()
        res = func(*args, **kwargs)
        print(f'calculation time ={time.time() - time_s}sec')
        return res
    return wrapper


@timer
def EWS_DNB(x, window_size, padding='online', normalization='straight'):
    print('caluculating time series DNB:')
    # normalization
    if normalization == 'std':
        x = x / x.std(0)
    elif normalization == 'minmax':
        x = x / (x.max(0) - x.min(0))
    elif normalization == 'PCA':
        if x.shape[1] < 10:
            raise NameError('low dimmention.')
            return -1
        pca = PCA(n_components=10)
        x = pca.fit_transform(x)
    elif normalization != 'straight':
        raise NameError('select \'straight\',\'PCA\', \'minmax\', or \'std\'')
        return -1
    # 1 dim or n dim
    if len(x.shape) == 1:
        xs = sliding_window(x, window_size)
        cov_time_tmp = xs.std(1)
    else:
        x = x.reshape(x.shape[0], -1)
        xs = sliding_window(x, (window_size, 1)).reshape(-1,
                                                         x.shape[1], window_size)
        cov_time_tmp = np.zeros(xs.shape[0])
        for i in tqdm.tqdm(range(0, cov_time_tmp.shape[0])):
            sigmas, _ = np.linalg.eigh(np.cov(xs[i]))
            cov_time_tmp[i] = sigmas.max()

    if padding == 'same':
        # padding marage data using the edge
        cov_time = np.zeros(x.shape[0])
        cov_time[window_size//2:-window_size//2+1] = cov_time_tmp
        cov_time[:window_size//2] = cov_time_tmp[0]
        cov_time[-window_size//2+1:] = cov_time_tmp[-1]
        return cov_time
    elif padding == 'online':
        # cov_time[t] is calculated as time-sereis data t - window_size : t
        cov_time = np.zeros(x.shape[0])
        cov_time[:window_size-1] = cov_time_tmp[0]
        cov_time[window_size-1:] = cov_time_tmp
        return cov_time
    elif padding == 'valid':
        return cov_time_tmp
    else:
        raise NameError('select \'same\', \'online\', or \'valid\' ')
        return -1


def CPDotsu(ews):
    def OtsuScore(data, thresh):
        w_0 = np.sum(data <= thresh)/data.shape[0]
        w_1 = np.sum(data > thresh)/data.shape[0]
        # check ideal case
        if (w_0 == 0) | (w_1 == 0):
            return 0
        mean_all = data.mean()
        mean_0 = data[data <= thresh].mean()
        mean_1 = data[data > thresh].mean()
        sigma2_b = w_0 * ((mean_0 - mean_all)**2) + \
            w_1 * ((mean_1 - mean_all)**2)

        return sigma2_b
    ths = (ews.max() - ews.min()) * np.arange(0, 1, 1e-4) + ews.min()
    scores = np.zeros(ths.shape[0])
    for i in range(ths.shape[0]):
        scores[i] = OtsuScore(ews, ths[i])
    y_ews = np.zeros(ews.shape[0])
    y_ews[ews > ths[scores.argmax()]] = 1

    max_time = ews.argmax()
    cp = max_time - y_ews[:max_time][::-1].argmin()
    return cp


@timer
def CPD_EWS(ews, cfg={'type': 'ar', 'dim': 2}, scope_range=np.inf):
    print('caluculating change point:')
    max_time = ews.argmax()
    window_size = min(scope_range, max_time)
    ews_calc = ews[max_time - window_size:max_time] / \
        ews[max_time - window_size:max_time].std()
    if cfg['type'] == 'peak':
        cp = max_time
    elif cfg['type'] == 'ohtsu':
        cp = max_time - window_size + CPDotsu(ews_calc)
    elif cfg['type'] == 'linear':
        algo = rpt.Dynp(model='linear', min_size=1, jump=1).fit(
            ews_calc.reshape(-1, 1))
        cp = max_time - window_size + algo.predict(1)[0]
    elif cfg['type'] == 'ar':
        algo = rpt.Dynp(model='ar', params={"order": cfg['dim']}).fit(ews_calc)
        cp = max_time - window_size + algo.predict(1)[0]
    else:
        raise NameError('select \'peak\',\'linear\',\'ar\', \'ohtsu\',')
        return -1
    return cp
