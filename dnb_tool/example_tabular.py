import os
import importlib.resources
import shutil
import argparse


def main():

    parser = argparse.ArgumentParser(
        description='This script generates example data and configuration file for the DNB tool for tabular data. The files will be placed under `input`.',
        add_help=True
    )
    _ = parser.parse_args()

    dirname = "input"
    try:
        os.makedirs(dirname, exist_ok=False)
    except FileExistsError as e:
        raise e

    filename_samples = [
        "sample_data_1.csv",
        "sample_data_2.csv",
    ]
    filename_default_params = "sample_params.json"

    for filename in filename_samples:
        with importlib.resources.files('dnb_tool').joinpath(f"datasets/data/{filename}").open("r") as f:
            with open(f"{dirname}/{filename}", "w") as g:
                shutil.copyfileobj(f, g)

    with importlib.resources.files('dnb_tool').joinpath(f"datasets/data/{filename_default_params}").open("r") as f:
        with open(f"{dirname}/{filename_default_params}", "w") as g:
            shutil.copyfileobj(f, g)
