#!/usr/bin/env python3

import os
import sys
import argparse
# import numpy as np
import pandas as pd
import seaborn as sns
# import matplotlib as mpl
from matplotlib import pyplot as plt
from argparse import RawTextHelpFormatter

"""
Future updates:
    - Add a description in the script
    - a 2-columns file to map user-defined names in the figure
"""


def read_ani(fh):
    ani_df = pd.read_table(fh, sep='\t', index_col=0)
    return ani_df


def plot_heatmap(df, out_base):

    g = sns.clustermap(data=df.multiply(100), metric="seuclidean",
                       standard_scale=None, figsize=(15, 15),
                       cmap='YlOrBr')

    g.fig.suptitle('ANI results (in % - pyANI)', y=1, fontsize=16)

    plt.savefig(out_base + ".png", dpi=300, facecolor='white')
    plt.savefig(out_base + ".svg")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('out_name', help='A prefix for the figure files')
    parser.add_argument('ani_matrix', help='A square matrix from PyANI')
    parser.add_argument('--table', help='A two columns table to change IDs '
                        'in heatmap, in TSV', metavar="")
    # parser.add_argument('--no_header', help='Do not print the headers',
    #                     default=False, action='store_true')

    args = parser.parse_args()

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    try:
        # Check input/output files
        if not os.path.isfile(args.ani_matrix):
            raise Exception("There is no file %s" % args.ani_matrix)
        if os.path.isfile(args.out_name + '.png'):
            raise Exception("The outfile is already present: %s\n"
                            % args.out_name)

        if args.table:
            if not os.path.isfile(args.table):
                raise Exception("There is no file %s" % args.table)

        # Read matrix
        ani_df = read_ani(args.ani_matrix)
        # Plot
        plot_heatmap(ani_df, args.out_name)

        print("Done: %s" % args.out_name + '.{png,svg}')

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)
