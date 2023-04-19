from .core import two_step
from .read_files import read_csv_and_split

from .visualize import plot_heatmap
from .visualize import plot_correlation


def isfloat(s):
    # check if s can be converted to floating point number
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


def get_float(d, key, default=None):
    # get the float value from dictionary, or default value when it is missing
    if key in d:
        return float(d[key])
    else:
        if default is None:
            return d[key]  # raise KeyError
        else:
            return float(default)


# fill missing parameters with default valuess
def set_auto_params(d):
    # the method for calculate deviation
    d["deviation_metric"] = d.get("deviation_metric", "mad")
    # the parameter for selecting fluctuating genes
    d["thres_gene_filtering"] = get_float(d, "thres_gene_filtering", 2)

    # the linkage parameters for clustering
    d["linkage_metric"] = d.get("linkage_metric", "spearman")
    d["linkage_method"] = d.get("linkage_method", 'average')
    d["linkage_threshold"] = get_float(d, "linkage_threshold", 0.75)

    # the parameter for selecting large clusters
    d["thres_cluster_selection"] = get_float(d, "thres_cluster_selection", 0.5)

    # whether the metrics for each DNB variable are output
    d["output_metrics"] = d.get("output_metrics", False)

    # whether plots are generated
    d["plot_correlation"] = d.get("plot_correlation", False)
    d["plot_heatmap"] = d.get("plot_heatmap", False)
    d["plot_file_prefix"] = d.get("plot_file_prefix", None)
    d["plot_file_suffix"] = d.get("plot_file_suffix", None)
    return d


def dnb_tb(filename, key_control, key_experimental, **kwargs_DNB):
    # read file and split to control and experimental
    df_c, df_e = read_csv_and_split(
        filename, key_control, key_experimental)

    # fill missing parameters with default values
    kwargs_DNB = set_auto_params(kwargs_DNB)

    # main routine
    # dnb: DataFrame for results
    # params: parameters used in the analysis
    #   (just for display)
    dnb, params, df_x = two_step(df_e, df_c, **kwargs_DNB)

    # if options are given, generate some plots
    if kwargs_DNB["plot_correlation"]:
        filename = kwargs_DNB["plot_file_prefix"]
        if not filename is None:
            filename = filename + "correlation"
            if kwargs_DNB.get("plot_file_suffix", None):
                filename = filename + "_" + kwargs_DNB["plot_file_suffix"]
            filename = filename + ".png"
        print(f"filename: {filename}")
        plot_correlation(df_x, dnb, filename=filename)

    if kwargs_DNB["plot_heatmap"]:
        filename = kwargs_DNB["plot_file_prefix"]
        if not filename is None:
            filename = filename + "heatmap"
            if kwargs_DNB.get("plot_file_suffix", None):
                filename = filename + "_" + kwargs_DNB["plot_file_suffix"]
            filename = filename + ".png"
        print(f"filename: {filename}")
        plot_heatmap(df_e, df_c, dnb, filename=filename)

    # keep the results with key(timestamp)
    return dnb, params
