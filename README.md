# Collection of general scripts for bioinformatics

## Python3 scripts

### Libraries

Here is a list of homemade libraries:

- `generic_utils.py`: provides generic functions that can be used in my other scripts

### Scripts for parsing

Here is a list of scripts used for different task. Note that the library
`generic_utils.py` cited above is **mandatory** for some of them!

- `ncbi_taxid_to_taxonomy.py`: take a NCBI _taxid_ as input and outputs the full
taxonomy. Several options are available. Uses the _ETE3_ toolkit.
- `assembly_statistics.py`: return some basic statistics for an assembly
- `get_pfam_specific_hmm.py`: extract a list of PFam profiles rom the IDs.
- `comparem_aai_result_to_matrix.py`: reformat the amino-acid identity (AAI)
results obtained by `comparem aai_wf`, as the table is not very easy to understand...
- `number_informative_site_alignment.py`: get the proportion of gaps for each
sequence in an alignment file, _Fasta_ format

## Snakefiles

### Run a workflow

In general, to run a _SnakeMake_ workflow, use:

```bash
conda activate snakemake

snakemake -s ~/bioinfoscripts/snakefiles/phylosift_run.smk  --config samples=samples.tsv outdir=result/00_test_pipeline
```

A list of interesting parameters:
- `--dry-run`, to test the behavior
- `-c`, `--cores`, the number of threads that _SnakeMake_ can use. The workflow
is distributed on this number of cores
- `--config param=value`, to pass expected parameters

### The list of wokflows

A list of SnakeMake scripts
- `snakefiles/phylosift_run.smk`: run _PhyloSift_ on a genome. This workflow
requires an input: a tab-separated file with 2 columns, with the genome identifier
\{tab\} `path/to/sequence/file.fa`, **without** column names. And pass this
information to the script with `--config samples=/path/to/my_samples.tsv`.
It is also possible to give an output directory with `--config outdir=path/to/dir`.
The number of thread to run_PhyloSift_ can be customised too, through
`--config thread={int}`.