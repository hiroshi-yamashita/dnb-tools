from .tabular.dnb_iterate import dnb_tb_iterate
from .tabular.read_files import check_input, get_filenames
import argparse
import json


def main():
    # set parser
    parser = argparse.ArgumentParser(
        description='This script analyze tabular data and output Synchronously Fluctuated Genes (SFGs), which are candidate variables of Dynamic Network Biomarker (DNB).',
        add_help=True
    )

    parser.add_argument('--input_path',
                        default="input",
                        help='the name of folder that contains input .csv files (default: %(default)s)')

    parser.add_argument('--config_file',
                        default=None,
                        help='specify parameters from JSON file. Run `make_example_dataset` to make an example configuration file')

    parser.add_argument('--prefix',
                        default="sample_data",
                        help='the prefix of input .csv files (default: %(default)s)')
    parser.add_argument('--key_control',
                        default="ctrl",
                        help='the columns that contains this are considered as control group (default: %(default)s)')
    parser.add_argument('--key_experimental',
                        default="expr",
                        help='the columns that contains this are considered as experimental group (default: %(default)s)')
    parser.add_argument('--ignore_extra_columns',
                        default=False,
                        action="store_true",
                        help='ignore columns not included in either control or experimental group (default: %(default)s)')
    parser.add_argument('--output_filename',
                        default="output.csv",
                        help='DNB calculated from each file are written to this file (default: %(default)s)')

    parser.add_argument('--deviation_metric',
                        choices=["mad", "std"],
                        default="mad",
                        help='the metric for deviation. "mad": median absolute deviation. "std": standard deviation. (default: %(default)s)')
    parser.add_argument('--thres_gene_filtering',
                        type=float,
                        default=2,
                        help='genes whose deviations in the experimental group are larger than X*100 %% of those in the control group are selected for DNB candidates. (default: %(default)s)')
    parser.add_argument('--linkage_metric',
                        choices=["spearman", "pearson"],
                        default="spearman",
                        help='metric used for clustering. "spearman": Spearman\'s rank correlation, "pearson": Pearson\'s correlation. (default: %(default)s)')
    parser.add_argument('--linkage_method',
                        default="average",
                        help='linkage method used for clustering. Please see the documentation of scipy.cluster.hierarchy. (default: %(default)s)')
    parser.add_argument('--linkage_threshold',
                        type=float,
                        default=0.75,
                        help='the threshold for cluster division (default: %(default)s)')
    parser.add_argument('--thres_cluster_selection',
                        type=float,
                        default=0.5,
                        help='clusters whose size is larger than X*100 %% of the maximum cluster size are selected for output. (default: %(default)s)')

    parser.add_argument('--output_metrics',
                        default=True,
                        action="store_true",
                        help='enable the output of detailed metrics for DNB candidates (default: enabled)')
    parser.add_argument('--no-output_metrics',
                        action="store_false",
                        help='disable the output of detailed metrics (default: enabled)')
    parser.add_argument('--plot_correlation',
                        default=True,
                        action="store_true",
                        help='enable the plot of correlations of DNB candidates (default: enabled)')
    parser.add_argument('--no-plot_correlation',
                        dest="plot_correlation",
                        action="store_false",
                        help='disble the plot of correlations of DNB candidates (default: enabled)')
    parser.add_argument('--plot_heatmap',
                        default=True,
                        action="store_true",
                        help='enable the plot of input values for DNB candidates (default: enabled)')
    parser.add_argument('--no-plot_heatmap',
                        dest="plot_heatmap",
                        action="store_false",
                        help='disable the plot of input values for DNB candidates (default: enabled)')
    parser.add_argument('--plot_file_prefix',
                        default=None,
                        help='(path and) prefix of filenames of plots (if None, they will be displayed on screen) (default: %(default)s)')

    args = parser.parse_args()

    print("*** Step 1: Configuration ***")
    # the name of folder that contains input .csv files
    input_path = args.input_path
    # the prefix of input .csv files
    prefix = args.prefix
    # the columns that contains this are considered as control group
    key_control = args.key_control
    # the columns that contains this are considered as experimental group
    key_experimental = args.key_experimental
    # ignore columns not included in either control or experimental group
    ignore_extra_columns = args.ignore_extra_columns
    # DNB calculated from each file are written to this file
    output_filename = args.output_filename
    kwargs_DNB = {
        # the metric for deviation. "mad": median absolute deviation. "std": standard deviation.
        "deviation_metric": args.deviation_metric,
        # genes whose deviations in the experimental group are larger than X*100 \% of those in the control group are selected for DNB candidates.
        "thres_gene_filtering": args.thres_gene_filtering,
        # metric used for clustering. "spearman": Spearman's rank correlation, "pearson": Pearson's correlation.
        "linkage_metric": args.linkage_metric,
        # linkage method used for clustering. Please see the documentation of scipy.cluster.hierarchy.
        "linkage_method": args.linkage_method,
        # the threshold for cluster division
        "linkage_threshold": args.linkage_threshold,
        # clusters whose size is larger than X*100 % of the maximum cluster size are selected for output.
        "thres_cluster_selection": args.thres_cluster_selection,
        # output detailed metrics for DNB candidates
        "output_metrics": args.output_metrics,
        # plot correlations of DNB candidates
        "plot_correlation": args.plot_correlation,
        # plot inputs for DNB candidates
        "plot_heatmap": args.plot_heatmap,
        # (path and) prefix of filenames of plots (if None, they will be displayed on screen)
        "plot_file_prefix": args.plot_file_prefix
    }

    if args.config_file:
        with open(args.config_file, "r") as f:
            config_json = json.load(f)
        input_path = config_json.pop("input_path", input_path)
        prefix = config_json.pop("prefix", prefix)
        key_control = config_json.pop("key_control", key_control)
        key_experimental = config_json.pop(
            "key_experimental", key_experimental)
        ignore_extra_columns = config_json.pop(
            "ignore_extra_columns", ignore_extra_columns)
        output_filename = config_json.pop("output_filename", output_filename)

        for k in kwargs_DNB:
            kwargs_DNB[k] = config_json.pop(k, kwargs_DNB[k])

        if len(config_json) > 0:
            k = next(iter(config_json))
            raise ValueError(f"invalid key is in configuration file: {k}")

    print(f"Load input from \"{input_path}/{prefix}...\"")

    print("*** Step 2: Obtain and check input files ***")
    keys, filenames = get_filenames(input_path, prefix)
    check_input(keys,
                filenames,
                key_control,
                key_experimental,
                ignore_extra_columns)

    print("**** Step 3: calculate SFGs (DNB candidate) ****")

    result = dnb_tb_iterate(keys,
                            filenames,
                            key_control,
                            key_experimental,
                            kwargs_DNB)

    print("**** Step 4: output result to csv file ****")

    result.to_csv(output_filename, index=False)
    print(f"Output file is \"{output_filename}\"")


if __name__ == "__main__":
    main()
