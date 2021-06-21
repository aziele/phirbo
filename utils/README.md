# Utility scripts to create BLAST-based ranked lists for Phirbo

Python scripts for creating ranked lists for viruses and prokaryotes based on their FASTA sequences and using BLAST.

## Input

You need two different directories containing only sequence data in FASTA format. One should contain your potential host genomes (one prokaryote per FASTA file), the other should contain viral genomes/contigs (one virus per FASTA file).

```
example/
├── host
│   ├── NC_022515.fna
│   ├── NC_022516.fna
│   ├── NC_022523.fna
│   ├── NC_022524.fna
│   ├── NC_022532.fna
│   ├── NC_022535.fna
│   ├── NC_022543.fna
│   ├── NC_022546.fna
│   ├── NC_022547.fna
│   ├── NC_022550.fna
│   ├── NC_022567.fna
│   ├── NC_022568.fna
│   ├── NC_022569.fna
│   ├── NC_022575.fna
│   ├── NC_022576.fna
│   ├── NC_022582.fna
│   ├── NC_022583.fna
│   ├── NC_022584.fna
│   ├── NC_022593.fna
│   └── NC_022600.fna
└── virus
    ├── NC_000866.fna
    ├── NC_000871.fna
    ├── NC_000872.fna
    ├── NC_000896.fna
    └── NC_000902.fna
```

## Usage

To create ranked lists, follow the next four steps. You can simply copy and paste the next five commands to the terminal.


#### 1. Create BLAST database of prokaryotic genomes

The following command will create a BLAST database from all host FASTA files in `example/host` directory. The BLAST database will be created in `out/db/` directory.

```bash
python makeblastdb.py --in example/host/ --out out/db/
```

#### 2. BLAST viruses against the database

The following command will run BLAST on every virus FASTA file in `example/virus` directory. BLAST output will be saved in `out/virus_blast` directory. By default, the script will run BLAST on all CPU threads you have available. However, you can specify the number of threads using `--num_threads`.

```bash
python blastn.py --task blastn --in example/virus/ --db out/db/ --out out/virus_blast
```

#### 3. BLAST hosts against the database

The following command will run BLAST on every host FASTA file in `example/host` directory. BLAST output will be saved in `out/host_blast` directory. By default, the script runs BLAST with `blastn` task. To speed up the BLAST searches you can use `--task dc-megablast` or `--task megablast`.

```bash
python blastn.py --task megablast --in example/host/ --db out/db/ --out out/host_blast --num_threads 4
```


#### 4. Create ranked lists for Phirbo

The following two commands will convert BLAST outputs into ranked lists. These ranked lists of viruses and hosts will be saved in two directories `out/virus_ranks` and `out/host_ranks`, respectively.

```bash
python rank.py --in out/virus_blast/ --out out/virus_ranks --num_threads 4
```

```bash
python rank.py --in out/host_blast/ --out out/host_ranks --num_threads 4
```

The `rank.py` script can group multiple genomes of the same prokaryotic species according to their first appearance in BLAST output. You would need to provide a text file that maps genome identifiers to prokaryote species name. Please follow the format in [example/groups.tx](./example/groups.txt)).

Then run `rank.py` with `-group` parameter.

```bash
python rank.py --in out/host_blast/ --out out/host_ranks --group example/groups.txt --num_threads 4 
```