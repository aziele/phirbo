# Phirbo

A tool to predict prokaryotic hosts for phage (meta)genomic sequences. To predict phage-host interactions Phirbo uses information on sequence similarity between phages and bacteria as well as among bacteria.


## Requirements

You'll need Python 3.6 or greater to run Phirbo. It is a stand-alone script and has no Python package dependencies (i.e., it only uses the standard library).


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

In order to link phage (*P*) to host (*H*) sequence through intermediate sequences, phage and host sequences need to be used as queries in two separate sequence similarity searches (e.g., BLAST) against the same reference database of prokaryotic genomes (*D*). One BLAST search is performed for phage query (*P*) and the other for host query (*H*). The two lists of BLAST results, *P → D* and *H → D*, contain prokaryotic genomes ordered by decreasing score. To avoid a taxonomic bias due to multiple genomes of the same prokaryote species (e.g., *Escherichia coli*), prokaryotic species can be ranked according to their first appearance in the BLAST list. In this way, both ranked lists represent phage and host profiles consisting of the ranks of top-score prokaryotic species. 

Phirbo estimates the phage-host relationship by comparing the content and order between phage and host ranked lists using [Rank-Biased Overlap (RBO)](http://dx.doi.org/10.1145/1852102.1852106) measure. Briefly, RBO fosters comparison of ranked lists of different lengths with heavier weights for matching the higher-ranking items. RBO ranges between `0` and `1`, where `0` means that the lists are disjoint (have no items in common) and `1` means that the lists are identical in content and order.

<p align="center"><img src="images/figure.png" alt="Phirbo overview" width="80%"></p>


## Input data
You need to provide ranked lists - separately in two directories - for phage and baterial genomes. Every genome should have its own ranked list in a text file. The text format lists baterial species separated by a new line (if two or more species are the same in rank they should be comma-separated in one line) (see [file format](example/virus/NC_000866.txt)).


## Quick usage

To run Phirbo provide two input directories (for phages and bacteria) containing your ranked lists, and an output file name.

```bash
phirbo.py example/virus/ example/host/ example/predictions.csv
```

This will output two files:
* `predictions.csv` containing phage-host predictions (i.e., a top score host for each phage). 
* `predictions.matrix.csv` containing a matrix of scores between every phage and every host (phages in columns, bacteria in rows).

## Full usage

```
usage: phirbo.py [-h] [--p P] [--k K] [--t NUM_THREADS]
                 virus_dir host_dir output_file

Phirbo (v1.0) predicts hosts from phage (meta)genomic data

positional arguments:
  virus_dir        Input directory w/ ranked lists for viruses
  host_dir         Input directory w/ ranked lists for hosts
  output_file      Output file name

optional arguments:
  -h, --help       show this help message and exit
  --p P            RBO parameter in range (0, 1) determines the degree of top-
                   weightedness of RBO measure. High p implies strong emphasis
                   on top ranked items [default = 0.75]
  --k K            Truncate all ranked lists to the first `k` rankings to
                   calculate RBO. To disable the truncation use --k 0 [default
                   = 30]
  --t NUM_THREADS  Number of threads (CPUs) [default = 32]
```