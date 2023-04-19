import numpy as np
import matplotlib.pyplot as plt


def plot_correlation(df_x, df_ret, filename=None):
    if df_x is not None:
        # calculate correlation matrix
        cor = np.corrcoef(df_x.loc[df_ret["dnb"].values].values)

        # display the correlation matrix
        plt.pcolormesh(cor, vmin=-1, vmax=1)
        plt.xlabel("gene index")
        plt.ylabel("gene index")

        # show or save plots
        plt.title("correlation matrix of DNB genes")
        plt.colorbar()
    else:
        _, _ = plt.subplots(1, 1, figsize=(5, 5))
        plt.title("no candidate remained after deviation filtering")
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename)
    plt.close()


def plot_heatmap(df_expr, df_ctrl, df_ret, filename=None):
    # take DNB variables for each group
    arr_dnb_expr = df_expr.loc[df_ret["dnb"].values].values
    arr_dnb_ctrl = df_ctrl.loc[df_ret["dnb"].values].values

    # normalize experimental and control data for each row based on control data
    offset = np.mean(arr_dnb_ctrl, axis=1)
    scale = np.std(arr_dnb_ctrl, axis=1)
    arr_dnb_expr = (arr_dnb_expr - offset[:, None]) / scale[:, None]
    arr_dnb_ctrl = (arr_dnb_ctrl - offset[:, None]) / scale[:, None]

    # calculate value range
    v0 = np.minimum(np.min(arr_dnb_expr), np.min(arr_dnb_ctrl))
    v1 = np.maximum(np.max(arr_dnb_expr), np.max(arr_dnb_ctrl))

    # generate plots
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))

    # 1st panel: experimental group
    axes[0].pcolormesh(arr_dnb_expr, vmin=v0, vmax=v1)
    axes[0].set_ylabel("gene index")
    axes[0].set_xlabel("patient index")
    axes[0].set_title("experimental group")

    # 2nd panel: control group
    axes[1].pcolormesh(arr_dnb_ctrl, vmin=v0, vmax=v1)
    axes[1].set_title("control group")
    axes[1].set_xlabel("patient index")

    # show or save plots
    fig.suptitle("relative expression of DNB genes")
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename)
    plt.close()
