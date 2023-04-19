import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster


def mad(df):
    # MAD: median absolute deviation
    return df.subtract(df.median(axis=1), axis=0).abs().median(axis=1)


def clustering(df, **kwargs):
    # clustering using `scipy.cluster.hierarchy`

    # preprocess of input values for linkage, that will performed with correlation metric
    if kwargs["linkage_metric"] == "spearman":
        df_x = df.rank(axis=1)
    elif kwargs["linkage_metric"] == "pearson":
        df_x = df.copy()
    else:
        metr = kwargs["linkage_metric"]
        raise ValueError(
            f"\"{metr}\" for linkage_metric is not supported. Please use \"spearman\" or \"pearson\".")

    # call `scipy.cluster.hierarchy.linkage`
    Z = linkage(df_x,
                metric="correlation",
                method=kwargs["linkage_method"])

    # call `scipy.cluster.hierarchy.fcluster` to obtain cluster labels
    label_arr = fcluster(Z,
                         1-kwargs["linkage_threshold"],
                         criterion='distance')

    # count variables in each cluster to obtain the cluster size
    freq_sr = pd.Series(label_arr).value_counts()

    # label_arr: series of cluster indices where the variables classified into
    # freq_sr: cluster sizes
    # df_x: variables after preprocess, that is fed into the clustring routines
    return label_arr, freq_sr, df_x


def two_step(df_expr, df_ctrl, **kwargs):

    # check the size of input
    # the minimum number of measurement is 4
    Ne, Nc = df_expr.shape[1], df_ctrl.shape[1]
    print(f"[Step 0]")
    print(f"Control group size is {Nc}")
    print(f"Experimental group size is {Ne}")
    if Ne < 4:
        raise ValueError(
            'experimental group has less than 4 samples. Check the input files and settings.')
    if Nc < 4:
        raise ValueError(
            'control group has less than 4 samples. Check the input files and settings.')

    ########
    #### step 1: deviation filtering ####
    ########
    if kwargs["deviation_metric"] == "mad":
        # median absolute deviation
        dev_expr = mad(df_expr)
        dev_ctrl = mad(df_ctrl)
    elif kwargs["deviation_metric"] == "std":
        # standard deviation
        dev_expr = df_expr.std(axis=1, ddof=0)
        dev_ctrl = df_ctrl.std(axis=1, ddof=0)
    else:
        #
        metr = kwargs["deviation_metric"]
        raise ValueError(
            f"\"{metr}\" for deviation_metric is not supported. Please use \"mad\" or \"std\".")

    # collect variables that fluctuates in experimental group
    # than in control group by a specified factor(`theta`)
    theta = kwargs["thres_gene_filtering"]
    # collect index of such genes
    sub_idx = df_expr.index[dev_expr > theta * dev_ctrl]
    print(
        f"[Step 1] {len(sub_idx)} genes that are flucuating in experimental group are selected")
    # if only too few variables satisfies the condition,
    # returns immediately.
    if len(sub_idx) < 2:  # 0 or 1
        ret = pd.DataFrame([], columns=["dnb", "cluster",
                           "clustersize", "dev_expr", "dev_ctrl"])
        return ret, kwargs, None
        # "dnb": dnb_labels,
        # "cluster": dnb_clusterids,
        # "clustersize": dnb_clustersizes,
        # "dev_expr": dnb_dev_expr,
        # "dev_ctrl": dnb_dev_ctrl,
        # return df_expr.index[0:0], kwargs, None

    ########
    #### step 2: clustering ####
    ########

    # take only variables that passed the 1st step
    df_sub_expr = df_expr.loc[sub_idx]

    # clustring
    # label_arr: series of cluster indices where the variables classified into
    # freq_sr: cluster sizes
    # df_x: variables after preprocess, that is fed into the clustring routines
    label_arr, freq_sr, df_x = clustering(df_sub_expr, **kwargs)
    print(f"[Step 2] Clustering. Cluster sizes are " +
          ", ".join([str(x) for x in sorted(freq_sr)[::-1][:5]]) + "...")

    # drop clusters that is small relatively to the largest one.
    th = kwargs["thres_cluster_selection"] * freq_sr.iat[0]
    print(f"Threshold of cluster size is {th:.1f}")

    # display the number of remaining clusters
    cluster_count = np.sum(freq_sr > th)
    print(f"{cluster_count} clusters are selected.")

    # drop variables included in the dropped clusters
    # and then, this is the indices of DNB variables
    dnb_idx = sub_idx[np.isin(label_arr, freq_sr.index[freq_sr > th])]
    # drop rows for dropped variables in deviation DataFrames
    dnb_dev_expr = dev_expr.loc[dnb_idx].values
    dnb_dev_ctrl = dev_ctrl.loc[dnb_idx].values

    # convert DNB indices to list
    dnb_labels = list(dnb_idx)
    # make the list of large clusters
    dnb_clusterids = list(
        label_arr[np.isin(label_arr, freq_sr.index[freq_sr > th])])
    # list of corresponding cluster sizes
    dnb_clustersizes = freq_sr[dnb_clusterids]

    # merge them into a result DataFrame
    df_ret = pd.DataFrame({
        "dnb": dnb_labels,
        "cluster": dnb_clusterids,
        "clustersize": dnb_clustersizes,
        "dev_expr": dnb_dev_expr,
        "dev_ctrl": dnb_dev_ctrl,
    })

    ########
    # post analysis
    ########

    # calculate correlation measure for each cluster
    df_ret_ = []
    for g, df_g in df_ret.groupby("cluster"):
        if df_g.shape[0] > 1:
            # calculate correlation matrix of the variables in the cluster
            cor = np.corrcoef(df_x.loc[df_g["dnb"].values].values)

            # take the upper triangle of the matrix and flatten to list
            cor_list = []
            for i in np.arange(cor.shape[0]-1):
                cor_list.extend(cor[i, (i+1):])
            # then calculate mean
            cor_mean = np.mean(cor_list)
        else:
            # if cluster consists of 1 variable, fill it with NaN.
            cor_mean = np.nan

        # write correlation measure to each row in the DataFrame of the cluster
        df_g["cor_mean"] = cor_mean
        # and keep it
        df_ret_.append(df_g)

    # merge the results to one DataFrame
    df_ret = pd.concat(df_ret_, axis=0).sort_values(
        "clustersize", ascending=False)

    # the metrics for each DNB variable are output only when the option "output_metrics" is given
    # otherwise, it is simplified to include only indices of DNB variables
    if not kwargs["output_metrics"]:
        df_ret = df_ret[["dnb"]]

    # df_ret: the DataFrame of result
    # kwargs: parameters used in the analysis, whose missing values are filled by default values,
    return df_ret, kwargs, df_x
