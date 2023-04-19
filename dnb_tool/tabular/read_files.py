import numpy as np
import pandas as pd
import os


########
#### collect input files ####
########

def isinteger(s):
    # check if s can be converted to int
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


def sort_keys(keys, values):
    # convert input lists to dictionary
    ret = {}
    for k, v in zip(keys, values):
        # if key represents an integer, convert to int
        if isinteger(k):
            k = int(k)
        ret[k] = v

    # check if all keys are the same type, specifically, int or string.
    if not (np.all([isinstance(k, int) for k in ret.keys()]) or
            np.all([isinstance(k, str) for k in ret.keys()])):
        raise ValueError(
            "numerical suffixes cannot be mixed with other suffixes")

    # return sorted keys and corresponding values
    keys_sorted = sorted(ret.keys())
    return keys_sorted, [ret[k] for k in keys_sorted]


def filter_by_prefix(x, prefix, suffix):
    # remove PREFIX and SUFFIX, and also delimiter "_" or "." between PREFIX and BODY.
    keys = []
    values = []
    for s in x:
        if s.startswith(prefix) and s.endswith(suffix):
            k = s.lstrip(prefix).rstrip(suffix).strip()
            if len(k) > 0 and (k[0] == "_" or k[0] == "."):
                k = k[1:]
            keys.append(k)
            values.append(s)
    # values: the list of inputs that matches the form of "PrefixBodySuffix", "Prefix_BodySuffix" or "Prefix.BodySuffix"
    # keys: the list of corresponding "Body"
    return keys, values


def get_filenames(path, prefix):
    # collect files that matches in the specified format.
    # format is:
    # "{path}/{prefix}{key}.csv",
    # "{path}/{prefix}_{key}.csv", or
    # "{path}/{prefix}.{key}.csv".

    # collect all files in `path`
    ls = os.listdir(path)
    # extract keys and sort them by keys
    keys, filenames = filter_by_prefix(ls, prefix, ".csv")
    keys, filenames = sort_keys(keys, filenames)
    # return keys and corresponding list of fullpaths
    return keys, [path + "/" + v for v in filenames]


########
#### split DataFrame ####
########


def filter_by_substr(x, substr):
    # collect all strings that includes `substr`
    ret = []
    for i, s in enumerate(x):
        if substr in s:
            ret.append((i, s))
    # return corresponding index and matched strings
    return [i for i, s in ret], [s for i, s in ret]


def split_dataframe(df, key_control, key_experimental):
    # filter column keys by whether it includes `key_control` or `key_experimental`
    columns = df.columns
    idx_c, column_c = filter_by_substr(columns, key_control)
    idx_e, column_e = filter_by_substr(columns, key_experimental)
    # split dataframe using the indices
    df_c = df.iloc[:, idx_c]
    df_e = df.iloc[:, idx_e]
    # df_c: DataFrame for control,
    # df_e: DataFrame for experimental
    return df_c, df_e


def read_csv_and_split(filename, key_control, key_experimental, ignore_extra_columns=True):
    # read csv file (use the first column as index)
    df = pd.read_csv(filename, index_col=0)

    # split into control and experimental by column name
    df_c, df_e = split_dataframe(
        df, key_control, key_experimental)

    def check_success(df, df_c, df_e):
        if ignore_extra_columns:
            return df_c.size != 0 and df_e.size != 0
        else:
            return (df_c.shape[1] + df_e.shape[1]) == df.shape[1]

    # transposed DataFrame is also accepted
    # if failed, try the transposed one
    if not check_success(df, df_c, df_e):
        df_c1, df_e1 = split_dataframe(df.T, key_control, key_experimental)
        # when success, overwrite the result
        if check_success(df.T, df_c1, df_e1):
            df_c, df_e = df_c1, df_e1
        else:
            if not ignore_extra_columns:
                raise ValueError(
                    "Data is not correctly classified as control or experimental. Check the `key_control' and `key_experimental' settings or the `ignore_extra_columns' setting.")
    return df_c, df_e

########
#### check input file format ####
########


def print_dataframe_summary(df):
    print(df.iloc[:5].T.iloc[:5].T)


def check_input(keys, filenames, key_control, key_experimental, ignore_extra_columns):
    # sample first file in the input dataset,
    # and check whether it is correctly splited to control and experimental
    # by displaying them.

    if len(filenames) == 0:
        raise ValueError("No input files")

    print("#### input files ####")
    print(filenames)

    print("#### the first input table (", filenames[0], ") ####")
    print_dataframe_summary(
        pd.read_csv(filenames[0], index_col=0))

    df_c, df_e = read_csv_and_split(
        filenames[0], key_control, key_experimental, ignore_extra_columns=ignore_extra_columns)
    print(f"#### control group (key=\"{key_control}\") ####")
    print_dataframe_summary(df_c)
    print(f"#### experimental group (key=\"{key_experimental}\") ####")
    print_dataframe_summary(df_e)

    for filename in filenames:
        df_c, df_e = read_csv_and_split(
            filename, key_control, key_experimental, ignore_extra_columns=ignore_extra_columns)
