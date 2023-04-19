import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .timeseries.dnb_ts import EWS_DNB, CPD_EWS


def main():
    # set parser
    parser = argparse.ArgumentParser(
        description='This script aims to create early warning signals for branches, based on Dynamic Network Biomarker (DNB) theory.',
        add_help=True
    )
    parser.add_argument('filename',
                        help='Target csv filename: the 1st raw is description, the 1st columns is time or steps, the second and subsequent lines are data.')

    parser.add_argument('--input_path',
                        default=".",
                        help='the name of folder that contains input .csv files (default: %(default)s)')
    parser.add_argument('--window_size',
                        default=100,
                        help='sindow size to calculate covarrience matrix')
    parser.add_argument('--padding',
                        default="online",
                        choices=["valid", "same", "online"],
                        help='padding controls the values of the time-series on both sides., valid: no padding, same: completing the numbers so that the output is centered, online: completing numbers so that outputs can be calculated online.')
    parser.add_argument('--normalization',
                        default="straight",
                        choices=["straight", "std", "minmax", "PCA"],
                        help='normalization type; straight: not normalized, std: std of the data become 1, minmax: the maximum error of data become 1, PCA: Dimensions are compressed by PCA (Output is 10 dimensions). ')
    parser.add_argument('--cfg',
                        default={'type': 'ar', 'dim': 1},
                        help='Config of change point detection methods; type: peak : bifucation point assume peak linear : Linear prediction, ar : AR model, Ohtsu :  01 detection using Ohtsu method, dim: order of the target model')
    parser.add_argument('--scope_range',
                        default=1000,
                        help='Range to probe the change point from the maximum')

    args = parser.parse_args()
    #### 2. Read data from the csv file ####

    input_path = args.input_path
    df = pd.read_csv(f"{input_path}/{args.filename}", index_col=0)
    x = df.values[:, 1:]

    # look the csv head data
    print('Data State')
    print(df.head(10))

    #### 3. Calculating the EWS and the candidate of the bifurcation point ####

    # calc ews
    ews = EWS_DNB(x, window_size=args.window_size,
                  padding=args.padding, normalization=args.normalization)

    # calc change point
    cp = CPD_EWS(ews, cfg=args.cfg, scope_range=args.scope_range)
    control = cp//2

    #### 4. Visualizing and save ####

    # Visualization
    print('Visualization')
    fig = plt.figure(figsize=(8, 5))
    plt.subplot(2, 1, 1)
    plt.grid()
    plt.plot(x)
    plt.ylabel('Feature', fontsize=16)
    plt.subplot(2, 1, 2)
    plt.grid()
    plt.plot(ews)
    plt.scatter(cp, ews[cp], color='red', label='candidate of bifurcation')
    plt.scatter(control, ews[control], color='blue',
                label='candidate of control')
    plt.legend(fontsize=16)
    plt.ylabel('$\lambda_{max}$(Covariance matrix)', fontsize=16)
    plt.xlabel('Step', fontsize=16)
    fig.tight_layout()
    fig.align_labels()
    plt.savefig('EWS_DNB.pdf', bbox_inches='tight')

    # Save data
    df_ews = pd.DataFrame(ews, columns=["EWS_DNB"])
    df_ews.to_csv('EWS_' + args.filename)

    # make DNB tools file
    print('Make DNB dataset')
    x_cp = x[cp-args.window_size:cp]
    x_control = x[control-args.window_size:control]

    columns = [f'ctrl_{i:06}' for i in range(
        x_control.shape[0])] + [f'expr_{i:06}' for i in range(x_cp.shape[0])]
    index = df.columns[1:]
    df_out = pd.DataFrame(np.r_[x_control, x_cp].T,
                          index=index, columns=columns)
    df_out.to_csv('DNB_' + args.filename)


if __name__ == "__main__":
    main()
