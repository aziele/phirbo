# Phirbo

A tool to predict prokaryotic hosts for phage (meta)genomic sequences. To predict phage-host interactions Phirbo uses information on sequence similarity between phage and bacteria as well as bacteria relatedness.

## Requirements

You need Python 3.6 or later to run Phirbo, which is a stand-alone script and has no Python package dependencies (i.e., it only uses the standard library).


## Installation

Since Phirbo is just a single script, no installation is required. You can simply clone it and run it:

```bash
git clone https://github.com/aziele/phirbo.git
phirbo/phirbo.py --help
```

If you plan on using it often, you can copy it to someplace in your PATH variable for easier access:

```bash
cp phirbo/phirbo.py ~/.local/bin
phirbo.py --help
```

## Method
Phirbo links phage to host sequences through intermediate, common reference sequences that are potentially homologous to both phage and host sequences. 

In order to link phage (*P*) to host (*H*) sequence through intermediate sequences, phage and host sequences need to be used as queries in two separate sequence similarity searches (e.g., BLAST) against the same reference database of prokaryotic genomes (*D*). One BLAST search is performed for phage (*P*) query and the other for (*H*) host query. The two lists of BLAST results, *P → D* and *H → D*, contain prokaryotic genomes ordered by decreasing score. To avoid a taxonomic bias due to multiple genomes of the same prokaryote species (e.g., *Escherichia coli*), prokaryotic species can be ranked according to their first appearance in the BLAST list (Fig. 1c). In this way, both ranked lists represent phage and host profiles consisting of the ranks of top-score prokaryotic species. 

Phirbo estimates the phage-host relationship by comparing the overlap between phage and host ranked lists using Rank-Biased Overlap (RBO) metric.

<img src="images/figure.png" alt="Phirbo overview">


## Quick usage

Provide two input directories containing ranked lists and an output file name.

```bash
phirbo.py example/virus/ example/host/ example/output.txt
```

## Full usage

```
usage: phirbo.py [-h] [--p P] [--k K] [--t NUM_THREADS]
                 virus_dir host_dir output_file

Phirbo predicts hosts from phage (meta)genomic data

positional arguments:
  virus_dir        Input directory w/ ranked lists for viruses
  host_dir         Input directory w/ ranked lists for hosts
  output_file      Output file name

optional arguments:
  -h, --help       show this help message and exit
  --p P            RBO weighting parameter in range (0, 1). High p implies
                   strong emphasis on top ranked items [default = 0.75]
  --k K            Truncate all ranked lists to the first `k` rankings to
                   calculate RBO. To disable the truncation use --k 0 [default
                   = 30]
  --t NUM_THREADS  Number of threads (CPUs) [default = 32]
```

Positional arguments:

* `virus_dir` and `host_dir` are directories containing ranked lists for each phage and candidate host. Each ranked list must be in a separate text file.
* `output_file`: file where phage-host predictions will be saved. Phage and host names will correspond to the names of the input files in `virus_dir` and `host_dir`.

Optional arguments:

* `--p` is a RBO weighting parameter in range from `0` to `1`. The paramter determines how steeply the weight declines (smaller the `p`, the more highly top results are weighted). When `p = 0`, only the top-ranked item is considered, and the RBO score is either zero or one.
* `--k` specifies the maximal number of ranking to consider for RBO calculation.
* `--t` controls how many threads are used for host prediction. Phirbo scales well in parallel, so use lots of threads if you have them.

