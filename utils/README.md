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

To create ranked lists, follow the next five steps. You can simply copy and paste next five commands to the terminal.


### 1. Create BLAST database of prokaryotic genomes

The following command will create a BLAST database from all host FASTA files in `example/host` directory.

```bash
python makeblastdb.py --in example/host/ --out out/db/
```

The BLAST database will be created in `out/db/` directory.


### 2. BLAST viruses against the database

The following command will run BLAST on every virus FASTA file in `example/virus` directory.

```bash
python blastn.py --task blastn --in example/virus/ --db out/db/ --out out/virus_blast
```

BLAST results will be saved in `out/virus_blast` directory. By default, the script will run BLAST on all CPU threads you have available. However, you can specify the number of threads using `--num_threads`.


### 3. BLAST hosts against the database

The following command will run BLAST on every host FASTA file in `example/host` directory.

```bash
python blastn.py --task megablast --in example/host/ --db out/db/ --out out/host_blast --num_threads 4
```

BLAST results will be saved in `out/host_blast` directory. To speed up the searches you can use `--task dc-megablast` or `--task megablast`.


### 4. Create ranked lists from BLAST results


```bash
python rank.py --in out/virus_blast/ --out out/virus_ranks --group example/groups.txt --num_threads 4
```

```bash
python rank.py --in out/host_blast/ --out out/host_ranks --group example/groups.txt --num_threads 4
```