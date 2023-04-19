from .dnb import dnb_tb
import pandas as pd
import yaml


def dnb_tb_iterate(keys, filenames, key_control, key_experimental, kwargs_DNB):
    # keys: keys for datasets, typically timestamps
    # filenames: corresponding input filenames
    # key_control, key_experimental: string by which the input columns are classified
    # kwargs_DNB: parameters passed to the main routine `two_step`
    ret = []
    # calculate DNB for each input file
    for i, kf in enumerate(zip(keys, filenames)):
        k, filename = kf
        dnb, params = dnb_tb(filename, key_control,
                             key_experimental, **kwargs_DNB)

        # after all inputs are processed, display parameters for the analysis
        if i == len(filenames)-1:
            print("parameters used for this run:")
            print("========")
            print(yaml.dump(params, default_flow_style=False))
            print("========")
        # keep the results with key(timestamp)
        df = dnb.copy()
        df["time_point"] = k
        ret.append(df)
    # merge the kept result into DataFrame
    ret = pd.concat(ret, axis=0).reset_index(drop=True)

    # remove index values for the result
    #   (just for display)
    ret.index = [""] * len(ret.index)

    return ret
