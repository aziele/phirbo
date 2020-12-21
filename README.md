# Phirbo

A tool to predict prokaryotic hosts for phage (meta)genomic sequences. To predict phage-host interactions Phirbo uses information on sequence similarity between phage and bacteria as well as bacteria relatedness.

## Requirements

You need Python 3.6 or later to run Phirbo, which is a stand-alone script and has no Python package dependencies (i.e., it only uses the standard library).


## Installation

Since Phirbo is just a single script, no installation is required. You can simply clone it and run it:

```bash
git clone https://github.com/aziele/phirbo.git
phirbo.py --help
```

## Usage

Provide two input directories containing ranked lists and an output file name.

```bash
phirbo.py example/virus/ example/host/ example/output.txt
```

### Full usage

```bash
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

