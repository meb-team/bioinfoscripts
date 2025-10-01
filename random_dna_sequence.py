#!/usr/bin/env python3

"""
This script generate a random DNA sequence. The length is"""

import sys
import random
import hashlib
import argparse
from argparse import RawTextHelpFormatter

# Define the four nucleotides
NUCLEOTIDES = ["A", "T", "C", "G"]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-l",
        help="Length of the DNA sequence [1000]",
        default=1000,
        type=int,
        metavar="",
        required=False,
    )
    args = parser.parse_args()

    ## The lines bellow made the script unusable
    # if len(sys.argv) == 1:  # In the case where nothing is provided
    #     parser.print_usage(file=sys.stderr)
    #     sys.exit(1)

    try:
        # Generate the sequence
        dna_sequence = "".join(random.choices(NUCLEOTIDES, k=args.l))

        # Generate a unique name for the sequence, with SHA256 HASH function
        seq_name = hashlib.sha256(dna_sequence.encode("utf-8")).hexdigest()

        # Print to STDOUT
        print(">", seq_name, sep="")
        print(dna_sequence)

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)

## Verify the distribution of each nucleotide
# count_A = dna_sequence.count('A')
# count_T = dna_sequence.count('T')
# count_C = dna_sequence.count('C')
# count_G = dna_sequence.count('G')
#
# print("\nNucleotide Counts:")
# print(f"A: {count_A}")
# print(f"T: {count_T}")
# print(f"C: {count_C}")
# print(f"G: {count_G}")
