#!/usr/bin/env python3
import os
import sys
import argparse
from argparse import RawTextHelpFormatter


def parse_list(infile):
    """ This function read the input list and return the result as a list"""
    mylist = list()
    with open(infile, 'r') as fi:
        for line in fi.readlines():
            mylist.append(line.rstrip().upper())

    if len(mylist) == 0:
        raise Exception("the list of Pfams IDs is empty. Exit")
    return mylist


def extract_pf_of_interest(pfam, domains):
    """Take the Pfam-A.hmm and a list of domain
        return a dict with the Pfam ID and all lines to reconstitute the
        HMM profile
    """
    # Setup
    res = dict()  # a dict to store the domains extracted
    profile = list()
    save_current = False
    current_pf_id = ""

    # Loop
    with open(pfam, 'r') as fi:
        for line in fi.readlines():
            line = line.rstrip()

            # Reach the end of the current profile
            if line == "//":
                if save_current:
                    # save it in the dict
                    res[current_pf_id] = profile + ['//\n']

                # Clean the variables FOR EACH PROFILE!! Otherwise the whole
                # file is printed at the end :clown:
                save_current = False
                profile = list()

            else:
                # Keep all lines to store the profile
                profile.append(line)

                # Get the name of the current PROFILE ==> Keep it or not?
                if line.startswith("ACC"):
                    # From "ACC   PF21734.1" to "PF21734"
                    current_pf_id = line.split(None)[-1].split(".")[0]
                    if current_pf_id in domains:
                        print("found %s" % current_pf_id)
                        # Turn ON the save && delete the PF from the list
                        save_current = True
                        domains.remove(current_pf_id)

    return res


def print_files(outdir, res):
    # Create the output
    os.makedirs(outdir)

    for pfam, lines in res.items():
        fo = open(outdir + '/' + pfam + '_profile.hmm', "w")
        fo.write('\n'.join(lines))
        fo.close()
    return True


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)

    parser.add_argument('-i', help='The Pfam-A.hmm file', metavar="",
                        required=True)
    parser.add_argument('--pf', help='a single-column file with the Pfam ID to'
                        ' extract.\nExpected format: "PF\\d{5}"', metavar="",
                        required=True)
    parser.add_argument('-o', help='Directory to store the single profiles',
                        metavar='', required=True)

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    try:
        # Output exists? Kill the script
        if os.path.isdir(args.o):
            raise Exception('The script does not overwrite files or ' +
                            'directories. Make sure the directory provided ' +
                            'DO NOT exists.')

        # Read the list of PF ids
        print("read the list of pfams")
        pf_list = parse_list(args.pf)

        # Parse the main Pfam file and extract the one we wants
        print('parse the master Pfam file')
        my_pfams = extract_pf_of_interest(args.i, pf_list)

        # Print
        print_files(args.o, my_pfams)

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)
