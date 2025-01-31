# Collection of general scripts and files for bioinformatics

## Ideas to implement

A simple script to remove sequences from a multifasta using its ID, without
external libraries like _BioPython_. This means write a sequence parser, test
the exact presence of identifier, and explicily tell the which sequence were
removed. Default will be an output in the STDOUT and information in the
STDERR. A file and logfile and be used too.

## Dotfiles

Examples of dotfiles in the directory `dotfiles/`. Do not forget to copy them
and add the caracteristic `.` prefix!

## _Conda_ environments

**IMPORTANT** : Some channels require a licence to use them, that's why I recently
updated my [_.condarc_](dotfiles/condarc). This
[blog post](https://juke34.github.io/fix-anaconda-licensing-issues/en/)
illustrates the problem and help to configure _Conda_. This
[other post](https://juke34.github.io/fix-anaconda-licensing-issues/en/pages/conda-channels/)
lists the licenced channels.

---

First a tips: _how activating environment in a BASH script?_ Here are two lines
to add **at the top of your script**:

```bash
CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh

# Then load one of your environment, eg:
conda activate MySuperEnvironment
```

Some scripts presented below require non-native Python libraries or external
tools. I provide recipes for the _Conda_ environments I used to use under the
`resource/` directory.  
To install such environment from a recipe, follow these instructions:

1. first I suggest you to use [mamba](https://mamba.readthedocs.io/en/latest/)
   as package manager which is orders of magnitude **faster** than _Conda_

```bash
conda install -n base -c conda-forge mamba
```

2. Install the environment from the _YML_ recipe

```bash
conda env create --solver libmamba -f /path/to/environment.yml -n MyEnvName
```

3. Activate your freshly installed environment

```bash
conda activate MyEnvName
```

For documentation about _Conda_ usage, I suggest you to have a look at the
[official documentation](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html).

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
- `get_pfam_specific_hmm.py`: extract a list of PFam profiles from the IDs.
- `comparem_aai_result_to_matrix.py`: reformat the amino-acid identity (AAI)
  results obtained by `comparem aai_wf`, as the table is not very easy to understand...
- `number_informative_site_alignment.py`: get the proportion of gaps for each
  sequence in an alignment file, _Fasta_ format

### Other purposes

- `generate_ICS_file.py`: aims to generate an _ICalendar_ (_ICS_) file with a
  collection of events, based on dates written in a text file. There is no may to change
  the name of the event, nor the schedule (8am - noon) - **WIP**

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
  The number of thread to run _PhyloSift_ can be customised too, through
  `--config thread={int}`.

## Miscelaneous

### Gererate URL to share files stored in _S3_

Here is the procedure to generate a temporary URL to download a **single** file
stored in a _S3_ bucket:

```bash
# Generate the link, replace 'http' by 'https'
s3cmd signurl S3://BUCKET/path/MyFile `date -d 'now + 7 days' +%s` | \
    sed 's/http:/https:/g'

# Download with wget OR curl
wget -O MyFile URL
curl -o MyFile URL
```

A full example:

```bash
# Get the list of files; 'microstore' is an alias to my S3 storage name
rclone ls microstore:for_data_sharing/ | cut -f 2 -d " " | \
    awk 'BEGIN{FS="/"}{print "for_data_sharing/" $0 "\t" $3}' \
    >metaplasmidomes_files.tsv

# Generate the links
while read file name
do
    s3cmd signurl S3://$file `date -d 'now + 7 days' +%s` | \
        sed 's/http:/https:/g' | awk -v file=$file -v name=$name \
        'BEGIN{}{print file "\t" name "\t" $0}' \
            >>metaplasmidomes_files_urls.tsv
    sleep 1
done < metaplasmidomes_files.tsv

# Download
while read file name url
do
    ## Uncomment the line with your preferred tool
    # wget -O $name $url
    # curl -o $name $url
    sleep 2 # because it always better to let server rest for some seconds
done < metaplasmidomes_files_urls.tsv
```

## Usage, Share and Contibutions

All resources available in this repository are released under the _GNU General_
_Public License v2.0_, see `LICENCE` for more details.

Any contribution is welcome!
