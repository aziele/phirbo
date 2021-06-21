#!/usr/bin/env python3

import argparse
import multiprocessing
from pathlib import Path
import subprocess

desc = f'Create ranking lists from BLAST results'
p = argparse.ArgumentParser(description=desc)
p.add_argument('-in', '--in', metavar='indir', dest='indir', required=True,
               help='Query directory w/ FASTA files')
p.add_argument('-o', '--out', metavar='outdir', dest='outdir', required=True,
               help='Output directory to store ranking lists (will be '
               'created if it does not exist)')
p.add_argument('--group',  dest='group', type=argparse.FileType('r'),
               help='Comma-separated file that maps genome id to group id'
               '(e.g., species name or taxId) [optional, but recommended]')
p.add_argument('--num_threads', dest='num_threads', type=int,
               default=multiprocessing.cpu_count(),
               help='Number of threads (CPUs) [default = %(default)s]')
args = p.parse_args()




in_path = Path(args.indir)
out_path = Path(args.outdir)
group = {}
if args.group:
    for line in args.group:
        cols = line.strip().split(',')
        genome_id = cols[0]
        group_id = cols[1]
        group[genome_id] = group_id


def read_blast(infile):
    d = {}
    fh = open(infile)
    for line in fh:
        sl = line.split()
        sid = sl[1].split('|')[0]
        evalue = float(sl[10])
        score = float(sl[11])
        if sid not in d:
            d[sid] = 0
        if score > d[sid]:
            d[sid] = score
    fh.close()
    return d

def group_ids(qd):
    d = {}
    if group:
        for sid, score in qd.items():
            group_id = group[sid]
            if group_id not in d:
                d[group_id] = 0
            if score > d[group_id]:
                d[group_id] = score
        return d
    return qd

def rank(qd):
    lst = list(qd.items())
    lst.sort(key=lambda x: (-x[1], x[0]))
    prev_score = 0
    r = 0
    d = {}
    for hid, score in lst:
        if score != prev_score:
            r += 1
            d[r] = []
        d[r].append(hid)
        prev_score = score
    return d



def rank_file(args):
    infile, outfile = args
    qd = read_blast(infile)
    qd = group_ids(qd)
    d = rank(qd)
    oh = open(outfile, 'w')
    for r in range(1, len(d)+1):
        oh.write(f'{",".join(d[r])}\n')
    oh.close()


out_path.mkdir(parents=True, exist_ok=True)

lst_query = []
for f in in_path.iterdir():
    genome_id = f.stem
    outfile = out_path.joinpath(f'{genome_id}.txt')
    lst_query.append((f, outfile))

with multiprocessing.Pool(args.num_threads) as pool:
    lst_result = pool.map(rank_file, lst_query)

