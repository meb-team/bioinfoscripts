#!/usr/bin/env python3

import sys
import argparse
from argparse import RawTextHelpFormatter
from ete3 import NCBITaxa


classic_ranks = ["superkingdom", "kingdom", "phylum", "class", "order",
                 "family", "genus", "species"]


def print_values(my_lineage, add_id='', headers=False, classic=False):
    """
    This function prints the result as a single line separated by tabs.
    It takes as input a list of lists, the inner size is 2.
    It can also print an extra field to add for example a custom id
    """
    index = 0 if headers else 1
    if classic:
        if headers:
            l1 = "custom_id\t" + "\t".join(classic_ranks) if add_id else \
                    "\t".join(classic_ranks)
            print(l1)
        else:
            # Sometimes the intermediates ranks are not present, so we have
            # to take this into account
            if add_id:
                print(add_id, end="\t")
            
            # A temporary dict for an easy access to ranks
            temp_d = {val[0]: val[1] for val in my_lineage}

            # Print
            for i in range(len(classic_ranks)):
                if classic_ranks[i] in temp_d.keys():
                    if i == len(classic_ranks) - 1:  # For the new line
                        print(temp_d[classic_ranks[i]])
                    else:
                        print(temp_d[classic_ranks[i]], end="\t")
                else:
                    if i == len(classic_ranks) - 1:  # For the new line
                        print()
                    else:
                        print("\t", end='')

    else:
        for i in range(len(my_lineage)):
            # Shall we add an identifier?
            if (i == 0) and (add_id != ''):
                if index == 0:
                    print("custom_id", end="\t")
                elif index == 1:
                    print(add_id, end="\t")

            if i == len(my_lineage) - 1:
                print(my_lineage[i][index])
            else:
                print(my_lineage[i][index], end='\t')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('taxid', help='NCBI taxid', type=int)
    parser.add_argument('--update', help='Update the local NCBI database',
                        default=False, action='store_true')
    parser.add_argument('--id', help='An ID to add as the first column',
                        default='', type=str)
    parser.add_argument('--no-clade', help='Remove the rank(s) "clade" from'
                        ' the lineage', default=False, action='store_true')
    parser.add_argument('--classic', help='only the following ranks are '
                        'returned (if available): ' +
                        " ; ".join(classic_ranks), action='store_true',
                        default=False)
    parser.add_argument('--no-header', help='Do not print the ranks names',
                        action='store_true', default=False)

    args = parser.parse_args()

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    try:
        # Some sanity checks:
        if args.classic:
            args.no_clade = True

        # Load the database
        ncbi = NCBITaxa()

        # If the user wants to update its local database
        if args.update:
            ncbi.update_taxonomy_database()

        # Get the full lineage of the given taxid
        lineage = ncbi.get_lineage(args.taxid)

        # Translate all taxids into the names
        names = ncbi.get_taxid_translator(lineage)

        # Get the ranks for each taxid in the lineage
        ranks = ncbi.get_rank(lineage)

        # Merge both informations, as a list of tuples
        my_lineage = [tuple(item) for item in zip(
                        [ranks[taxid] for taxid in lineage],
                        [names[taxid] for taxid in lineage])]
        # Delete ranks named 'no rank'
        # ## Pop items from the end of the list, otherwise it is a big messed
        # ## with the indices!
        # ## The user can choose to drop ranks called "clade"

        for i in range(len(my_lineage) - 1, -1, -1):
            # Case where the user asked for a "classic" taxonomy
            if args.classic:
                if my_lineage[i][0] not in classic_ranks:
                    del my_lineage[i]
            else:
                # Make the checks for the other cases
                if my_lineage[i][0] == 'no rank':
                    del my_lineage[i]
                if (args.no_clade) and (my_lineage[i][0] == 'clade'):
                    del my_lineage[i]

        # Print the result
        if not args.no_header:
            # Enter this block if user do not specify "--no-header"
            print_values(my_lineage, add_id=args.id, headers=True,
                         classic=args.classic)
        print_values(my_lineage, add_id=args.id, classic=args.classic)

        """
        This is a way of printing the FULL lineage:
            print('\t'.join([ranks[taxid] for taxid in lineage]))
            print('\t'.join([names[taxid] for taxid in lineage]))
            """

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)
