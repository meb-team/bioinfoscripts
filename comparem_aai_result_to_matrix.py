#!/usr/bin/env python3
"""Reformat a result table from 'CompareM aai_wf'"""

import os
import sys
import argparse
from argparse import RawTextHelpFormatter

import numpy as np
import pandas as pd


def diff_list(lst1, lst2):
    """Find the item from list 1 NOT present in list 2"""
    for elt in lst1:
        if elt not in lst2:
            return elt


if __name__ == "__main__":
    __description__ = "Reformat a result table from 'CompareM aai_wf', " \
                      "output in the same directory as input"
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                     description=__description__)
    parser.add_argument('table', help='Comparem aai_wf result table')

    args = parser.parse_args()

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    try:
        if not os.path.isfile(args.table):
            raise Exception("There is no file %s" % args.table)

        # Read the file
        aai_tab = pd.read_table(args.table)
        # Reshape the matrix
        df = aai_tab.pivot(index='#Genome A', columns='Genome B',
                           values='Mean AAI').fillna(0).copy()

        # Then, I have to find the genome not present in rows, and same for
        # the one absent from columns
        common_genomes = np.intersect1d(aai_tab['#Genome A'].unique().tolist(),
                                        aai_tab['Genome B'].unique().tolist(),
                                        assume_unique=True).tolist()

        # To find the genome not present in rows, I have to identify the genome
        # present from "Genome B" but absent from the intersection of both datasets
        not_in_col = diff_list(aai_tab['#Genome A'].unique().tolist(),
                               common_genomes)
        not_in_row = diff_list(aai_tab['Genome B'].unique().tolist(),
                               common_genomes)

        # Add the column
        df[not_in_col] = np.zeros(len(df.index))

        # Add the row: I have to concatenate two dataframes
        temp = pd.DataFrame(dict(zip(df.columns , np.zeros(len(df.columns)))),
                            index=[not_in_row])
        df = pd.concat([df, temp], axis=0)
        del(temp)

        # Sorting the columns based on the index
        df = df.reindex(columns=df.index)

        # At this point, we have a semi-matrix, let's make it complete and
        # symetric to replace the zeros in the diagonal by 100
        aai = df + df.T
        aai.replace({0:100}, inplace=True)

        # Save
        outpath = os.path.dirname(args.table)
        outname = '.'.join(os.path.basename(args.table).split('.')[:-1]) + \
                    '.reformat.tsv'

        aai.to_csv(outpath + '/' + outname, sep='\t')

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)

