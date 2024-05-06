#!/usr/bin/env python3

""" This script compute the proportion of informative site in a Fasta alignment,
for each sequence
"""

import os
import sys
import argparse
from argparse import RawTextHelpFormatter
from Bio import SeqIO
import generic_utils as gu


def read_fasta_alignment(file_name):
    """Read a Fasta file"""
    # Check
    gu.is_file_exists(file_name)

    # Read
    d = {}
    records = SeqIO.parse(file_name, 'fasta')
    for record in records:
        d[record.id] = record.seq

    return d


def check_seq_length(seq_d):
    """Verify that all sequences present in the alignment have the same
    length"""

    sizes = []
    for seq in seq_d.values():
        sizes.append(len(seq))

    if len(set(sizes)) > 1:
        # There are sequences with unequal length in the alignment
        # Browse the sequences, get their size, store the ids in a dict
        aln_d = {}
        for seqid, seq in seq_d.items():
            size = len(seq)
            try:
                aln_d[size] += [seqid]
            except KeyError:
                aln_d[size] = [seqid]

        # Identify the most abudant alignment length
        most_abundant_length = 0
        most_abundant_length_name = ''
        for aln_size, seq_ids in aln_d.items():
            # print(aln_size, seq_ids)
            if len(seq_ids) > most_abundant_length:
                most_abundant_length = len(seq_ids)
                most_abundant_length_name = aln_size

        message = "Some of your sequences have different length. The most " + \
            "common is " + str(most_abundant_length_name) + \
            f", with {most_abundant_length}/{len(seq_d)} sequences.\n"
        message += "Here is an example of sequence with a different length:\n"

        for k in aln_d:
            if k != most_abundant_length_name:
                key_for_example = k
                break
        message += f" - {aln_d[key_for_example][0]} has a length of " + \
            str(key_for_example)

        # Raise the error
        raise Exception(message)

    return True


def prop_informative_sites(seq_d, outfile):
    """Compute the proportion of informative sites aka 
    1 - (number gaps / alignment length)"""

    if outfile:
        fo = open(outfile, 'w', encoding='utf-8')
    else:
        fo = sys.stdout

    # Headers
    print("seq_id", "prop_informative_site", sep="\t", file=fo)

    # Body
    for seqid, seq in seq_d.items():
        gaps = len(seq) - len(seq.replace('-', ''))  # Full - without gaps
        prop_informative = 1 - (gaps / len(seq))
        print(seqid, str(prop_informative), sep='\t', file=fo)

    if outfile:
        fo.close()

    return True


if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('alignment', help='Alignment file, in Fasta')
    parser.add_argument('-o', help='File to write the results. Default is '
                        'STDOUT', required = False, metavar="")

    args = parser.parse_args()

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    try:
        # Read, check alignment and outfile if provided
        seqs = read_fasta_alignment(args.alignment)
        check_seq_length(seqs)
        if args.o:
            if os.path.exists(args.o):
                raise FileExistsError('Outfile exists but this script does not'
                                      'overwright things')

        # The core of this script
        prop_informative_sites(seqs, args.o)

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)
