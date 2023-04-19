import pandas as pd
import numpy as np

import argparse
import os

from dnb_tool.datasets import saddle_node_model
from dnb_tool.datasets import May_model
from dnb_tool.datasets import HP_model


def main():
    parser = argparse.ArgumentParser(
        description='This script generates example data for the DNB tool for timeseries data. The files will be placed under `input`.',
        add_help=True
    )
    parser.add_argument('--saddle_node',
                        default=False,
                        action="store_true",
                        help='Toy model with saddle node bifurcation')
    parser.add_argument('--may',
                        default=False,
                        action="store_true",
                        help='May model')
    parser.add_argument('--hp',
                        default=False,
                        action="store_true",
                        help='A spatial harvested population model')
    args = parser.parse_args()

    model = None
    if args.saddle_node:
        if model:
            raise ValueError("Multiple models specified")
        model = "saddle_node"
    if args.may:
        if model:
            raise ValueError("Multiple models specified")
        model = "may"
    if args.hp:
        if model:
            raise ValueError("Multiple models specified")
        model = "hp"

    dirname = "input"
    try:
        os.makedirs(dirname, exist_ok=False)
    except FileExistsError as e:
        raise e

    if model == "saddle_node":
        # Toy model with saddle node bifurcation
        times, x, y = saddle_node_model.get_data()
    elif model == "may":
        # May model [2]
        times, x, y = May_model.get_data()
    elif model == "hp":
        # A spatial harvested population model[3]
        HP_model.overview()
        times, x, y = HP_model.get_data(n=5, sigma=0.1)
    else:
        raise ValueError("No models specified")

    df = pd.DataFrame(np.c_[times, x])
    df.to_csv(f'{dirname}/sample.csv', index=False)
