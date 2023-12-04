import os
import glob
import pandas as pd
from snakemake.utils import validate

# config file
"""
There is no plan to setup a config file, however the user must pass some arguments
through `--config` like:
- samples=/path/to/samples/file.tsv
- outdir (not mandatory, default = ".")

Some sources:
- https://stackoverflow.com/questions/54095096/snakemake-and-pandas-syntax-getting-sample-specific-parameters-from-the-sample
- https://github.com/snakemake-workflows/rna-seq-star-deseq2
"""

# Path of the executable
exec_phylosift = os.path.expanduser('~') + '/bioware/PhyloSift/phylosift'

# Read a Two-fields tab file WITHOUT headers
samples = (
    pd.read_csv(config["samples"], sep="\t", names = ['accession', 'sequence'])
    .set_index("accession", drop=False)
)

# Several validations
validate(config, "schema_yml/phylosift.config.yml")
validate(samples, "schema_yml/phylosift.samples.yml")

# Constraint the wildcard Accession to match something in the list of samples
wildcard_constraints:
    accession = "|".join(samples.index.tolist()),
    outdir = str("|" + config['outdir']).join(samples.index.tolist())

# The main part
rule all:
    input:
        expand("{outdir}/{accession}/04_clean.done",
                outdir=config["outdir"], accession=samples.index.tolist())

rule run_phylosift:
    input:
        sequence = lambda wildcards: samples.loc[wildcards.accession, 'sequence']
    output:
        directory(config["outdir"] + "/" + "{accession}"),
        touch(temp(config["outdir"] + "/{accession}/00_run.done"))
    params:
        threads = config['threads']
    run:
        cmd = f"{exec_phylosift} search --isolate --besthit " + \
            "--disable_updates --threads {params.threads} " + \
            "--output {output[0]} {input.sequence}"
        shell(cmd)

def identify_a_marker(result_path, seq_acc, full_path=False):
    """ This function identify the name of a marker. This is mandatory to
    continue the run
    """
    if not os.path.isdir(result_path):
        raise IsADirectoryError('The output directory %s is not reachable'
                                % result_path)

    markers = glob.glob(result_path.rstrip() + "/" + seq_acc +
                        "/" + "blastDir/*lastal.candidate.aa*")
    if len(markers) > 0:
        if full_path:
            return markers[0]
        else:
            return os.path.basename(markers[0])
    else:
        return False

rule check_phylosift:
    """Check PhyloSift found at least **1** marker for the current genome"""
    input:
        prev_step = ancient(config["outdir"] + "/{accession}/00_run.done"),
        sequence = lambda wildcards: samples.loc[wildcards.accession, 'sequence'],
    output:
        touch(temp(config["outdir"] + "/{accession}/01_check.done"))
    params:
        seq_acc = lambda wc: wc.get('accession')
    run:
        marker = identify_a_marker(config["outdir"], params.seq_acc)
        if not marker:
            raise Exception('Phylosift did not identify marker in the current'
                            ' genome %s' % {wildcards.accession})
        else:
            cmd = f"touch {config['outdir']}/{wildcards.accession}" + \
                  "/{marker}.marker"
            shell(cmd)

rule align_phylosift:
    """Align the marker found by PhyloSift"""
    input:
        sequence = lambda wildcards: samples.loc[wildcards.accession, 'sequence'],
        prev_step = ancient(config["outdir"] + "/{accession}/01_check.done"),
    output:
        touch(temp(config["outdir"] + "/{accession}/02_align.done"))
    params:
        threads = config['threads']
    run:
        marker_found = glob.glob(config["outdir"] + \
                                 f"/{wildcards.accession}/*.marker")[0]
        marker_path = os.path.dirname(marker_found) + '/blastDir/' + \
                      os.path.basename(marker_found.replace('.marker', ''))

        cmd = f"{exec_phylosift} align --isolate --besthit " + \
              f"--disable_updates --threads {params.threads} " + \
              f"--output {config['outdir']}/{wildcards.accession} " + \
              f"{marker_path}"
        shell(cmd)

rule rename_phylosift:
    """Rename the sequences, as PhyloSift gives them temporary IDs"""
    input:
        sequence = lambda wildcards: samples.loc[wildcards.accession, 'sequence'],
        prev_step = ancient(config["outdir"] + "/{accession}/02_align.done")
    output:
        touch(temp(config["outdir"] + "/{accession}/03_rename.done"))
    params:
        threads = config['threads']
    run:
        marker_found = glob.glob(config["outdir"] + \
                                 f"/{wildcards.accession}/*.marker")[0]
        marker_path = os.path.dirname(marker_found) + '/blastDir/' + \
                      os.path.basename(marker_found.replace('.marker', ''))

        cmd = f"echo {marker_path}; "
        cmd += f"{exec_phylosift} name --isolate --besthit " + \
              f"--disable_updates --threads {params.threads} " + \
              f"--output {config['outdir']}/{wildcards.accession} " + \
              f"{marker_path}"
        shell(cmd)

rule clean:
    input:
        prev_step = ancient(config["outdir"] + "/{accession}/03_rename.done")
    output:
        touch(temp(config["outdir"] + "/{accession}/04_clean.done"))
    run:
        marker_found = glob.glob(config["outdir"] + \
                            f"/{wildcards.accession}/*.marker")[0]
        cmd = f"rm {marker_found}"
        shell(cmd)
