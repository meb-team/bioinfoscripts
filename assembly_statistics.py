#!/usr/bin/env python3

import os
import sys
import gzip
import argparse
from Bio import SeqIO
from argparse import RawTextHelpFormatter


def is_gz_file(filepath):
    with gzip.open(filepath, 'r') as fh:
        try:
            # Gzip file
            fh.read(1)
            return 'rt'
        except gzip.BadGzipFile:
            # regular file
            return 'r'


def fasta_to_seq_dict(asm):
    """Return a dictionnary contig:sequence"""
    read_mode = is_gz_file(asm)
    contigs = dict()
    if read_mode == 'rt':
        fi = gzip.open(asm, read_mode)
    else:
        fi = open(asm, read_mode)

    records = SeqIO.parse(fi, 'fasta')

    # Get the list
    for record in records:
        contigs[record.id] = str(record.seq)
    fi.close()

    return contigs


def get_total_length(seq_d, contig_list=False):
    """Return the assembly length"""
    contigs_size = list()
    total_length = 0

    for contig, seq in seq_d.items():
        total_length += len(seq)
        contigs_size.append(len(seq))

    if contig_list:
        return total_length, contigs_size
    else:
        return total_length


def get_N50_L50(seq_d):
    """Return the N50 and the L50"""
    total_length, contigs_size = get_total_length(seq_d, contig_list=True)

    # Sort the list
    contigs_size.sort(reverse=True)

    n50 = 0
    l50 = 0
    cumul_length = 0
    for i in range(0, len(contigs_size)):
        cumul_length += contigs_size[i]
        if cumul_length >= (total_length / 2):
            n50 = contigs_size[i]
            l50 = i + 1
            break

    return n50, l50


def get_GC_content(seq_d):
    """ Return the G+C content of the assembly"""
    num_G_and_C = 0
    total_length = 0

    for contig, seq in seq_d.items():
        total_length += len(seq)

        for nt in seq.upper():
            if nt == "G":
                num_G_and_C += 1
            elif nt == "C":
                num_G_and_C += 1
    value = (num_G_and_C / total_length) * 100
    return float(f"{value:.2f}")


def get_extreme_contigs(seq_d):
    """Return the length of the longest and the smallest contigs"""
    contigs_size = list()

    for contig, seq in seq_d.items():
        contigs_size.append(len(seq))

    contigs_size.sort(reverse=True)
    if len(contigs_size) == 1:
        return contigs_size[0], contigs_size[0]
    else:
        return contigs_size[0], contigs_size[-1]


def _append_list(l1, v1, l2, v2):
    l1.append(v1)
    l2.append(v2)
    return l1, l2


def print_result(name, total_l=None, n50=None, l50=None, gc=None, longest=None,
                 smallest=None):
    """Print the result """
    headers, values = ['assembly'], [name]

    if total_l:
        headers, values = _append_list(headers, 'lentgh', values, total_l)
    if n50:
        headers, values = _append_list(headers, 'N50', values, n50)
    if l50:
        headers, values = _append_list(headers, 'L50', values, l50)
    if gc:
        headers, values = _append_list(headers, 'GC_content', values, gc)
    if longest:
        headers, values = _append_list(headers, 'longest_contig', values,
                                       longest)
    if smallest:
        headers, values = _append_list(headers, 'smallest_contig', values,
                                       smallest)

    print("\t".join(headers), "\n", "\t".join(values), sep='')
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('assembly', help='Genome assembly in fasta[.gz]')
    parser.add_argument('--name', help='A name to recognize the assembly '
                        '- ["assembly"]', default="assembly", metavar="")
    parser.add_argument('--only', help='Turn ON the choice of statistic to '
                        'return', default=False, action='store_true')
    parser.add_argument('--length', help='Total length', default=False,
                        action='store_true')   
    parser.add_argument('--n50', help='Get the N50 and the L50',
                        default=False, action='store_true')
    parser.add_argument('--gc', help='Get the G+C content', default=False,
                        action='store_true')
    parser.add_argument('--extreme_contigs', help='Return the size of the '
                        'longest and smallest contigs', default=False,
                        action='store_true')

    args = parser.parse_args()

    if len(sys.argv) == 1:  # In the case where nothing is provided
        parser.print_usage(file=sys.stderr)
        sys.exit(1)

    try:
        if not os.path.isfile(args.assembly):
            raise Exception("There is no file %s" % args.assembly)

        # Init variables
        contigs = fasta_to_seq_dict(args.assembly)
        total_l, n50, l50 = None, None, None
        gc_cont, longest, smallest = None, None, None

        # Get values
        if args.only:
            if args.n50:
                n50, l50 = get_N50_L50(contigs)
            if args.gc:
                gc_cont = get_GC_content(contigs)
            if args.extreme_contigs:
                longest, smallest = get_extreme_contigs(contigs)

        else:
            total_l = get_total_length(contigs)
            n50, l50 = get_N50_L50(contigs)
            longest, smallest = get_extreme_contigs(contigs)
            gc_cont = get_GC_content(contigs)

        # Print
        print_result(args.name, total_l=total_l, n50=n50, l50=l50, gc=gc_cont,
                     longest=longest, smallest=smallest)

    except Exception as e:
        # Something went wrong with the arguments?!
        print(e)
        sys.exit(1)
