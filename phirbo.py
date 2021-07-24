#!/usr/bin/env python3

import argparse
import math
import multiprocessing
from pathlib import Path
from typing import List, Set, Union, Dict

import numpy as np
import pandas as pd

__version__ = '1.0'


def get_arguments():
    desc = f'Phirbo (v{__version__}) predicts hosts from phage (meta)genomic data'
    p = argparse.ArgumentParser(description=desc)
    p.add_argument('virus_dir', metavar='virus_dir',
                   help='Input directory w/ ranked lists for viruses')
    p.add_argument('host_dir', metavar='host_dir',
                   help='Input directory w/ ranked lists for hosts')
    p.add_argument('out', metavar='output_file', type=argparse.FileType('w'),
                   help='Output file name')
    p.add_argument('--p', dest='p', type=float, default=0.75, metavar=None,
                   help='RBO parameter in range (0, 1) determines the degree of '
                   'top-weightedness of RBO measure. High p implies strong '
                   'emphasis on top ranked items [default = %(default)s]')
    p.add_argument('--k', dest='k', type=int,
                   default=30, help='Truncate all ranked lists to the first `k` '
                   'rankings to calculate RBO. To disable the truncation use '
                   '--k 0 [default =  %(default)s]')
    p.add_argument('--t', dest='num_threads', type=int,
                   default=multiprocessing.cpu_count(),
                   help='Number of threads (CPUs) [default = %(default)s]')
    p.add_argument('--version', action='version',
                   version='Phirbo v' + __version__,
                   help="Show tool's version number and exit")
    args = p.parse_args()
    return args


def rbo_wrap(hi, vi, p=0.75):
    hname = hnames[hi]
    vname = vnames[vi]
    return hi, vi, rbo(hd[hname], vd[vname], p=p)

def rbo(l1: List[Set[Union[str, int]]],
        l2: List[Set[Union[str, int]]],
        p: float = 0.75) -> float:
    """
    Rank-biased overlap (RBO) of two ranked lists that accounts for ties.
    RBO ranges between 0 and 1, where 0 means that the ranked lists are
    disjoint (have no items in common) and 1 means that the lists are
    identical in content and order.

    This function implements the extrapolated version of rbo. For details
    see equation (32) in http://doi.acm.org/10.1145/1852102.1852106.

    >>> lst1 = [{'c', 'a'}, {'b'}, {'d'}]
    >>> lst2 = [{'a'}, {'c', 'b'}, {'d'}]
    >>> rbo(lst1, lst2, p=0.9)
    0.9666666666666667

    >>> lst1 = [{1}, {2, 3}, {5}, {6}, {7}]
    >>> lst2 = [{1}, {2, 4}, {5, 6}]
    >>> rbo(lst1, lst2)
    0.8161576704545455
    """

    # Figure out the short (S) and long (L) list.
    sl, ll = sorted([(len(l1), l1), (len(l2), l2)])
    s, S = sl
    l, L = ll

    # Items from short/long list (`ss`/`ls`) till a given depth (ranking).
    ss = set()
    ls = set()
    x_d = {0: 0}  # No. of shared items between `S` and `L` till a given depth.
    # No. of items in `S`/`L` till a given depth.
    len_ss = {0: 0}
    len_ls = {0: 0}
    sum1 = 0
    # Iterate over depths of a longer list.
    for i in range(l):
        d = i + 1

        xset = L[i]
        yset = S[i] if i < s else None

        ls.update(xset)
        if yset is not None:
            ss.update(yset)

        x_d[d] = x_d[d-1]   # Last common overlap.
        len_ss[d] = len_ss[d-1]
        len_ls[d] = len_ls[d-1]

        for x in xset:
            # If the new item from `L` is in `S` already.
            x_d[d] += 1 if x in ss else 0
            len_ls[d] += 1
        # If still have a shorter list.
        if yset is not None:
            for y in yset:
                # If the new item from `S` is in `L` already.
                x_d[d] += 0 if y not in ls or y in xset else 1
                len_ss[d] += 1
        # Agreement is a proportion of shared items between
        # two ranked lists at given depth.
        agreement = (2 * x_d[d] / (len_ss[d] + len_ls[d]))
        sum1 += p ** d * agreement

    agreement = (2 * x_d[s] / (len_ss[s] + len_ls[s]))
    x_s = agreement * s
    sum2 = sum([p ** d * x_s * (d - s) / s / d for d in range(s+1, l+1)])
    term1 = (1 - p) / p * (sum1 + sum2)

    agreement = (2 * x_d[l] / (len_ss[l] + len_ls[l]))
    x_l = agreement * s
    term2 = p ** l * ((x_l - x_s) / l + x_s / s)
    return term1 + term2


def weight(d: int, p: float) -> float:
    """
    Weight of ranks from 1 to `d` used in RBO score calculation. Parameter p
    determines the degree of top-weightedness of the RBO metric.

    The weight of the prefix of length `d` is the sum of the weights of the
    ranks to that depth. The weight specifies the contibution of these ranks
    to the overall RBO score.

    >>> weight(10, 0.9)
    0.86

    It means that for p = 0.9, first 10 ranks have 86% of the weight
    (contribuion) in the RBO score.

    REFERENCE:
    http://doi.acm.org/10.1145/1852102.1852106 (Equation 21 in the paper)

    """
    p1 = 1 - pow(p, d-1)
    p2 = ((1-p)/p)*d
    p3 = math.log(1.0/(1-p))
    p4 = sum([pow(p, i)/i for i in range(1, d)])
    weight = p1 + p2 * (p3-p4)
    return weight


def read_list(filename: Union[str, Path], k: int = 0) -> List[Set[str]]:
    """Read a ranked list from a file."""
    fh = open(filename)
    lst = [set(l.strip().split(',')) for l in fh]
    fh.close()
    return lst[:k] if k else lst


def get_lists(directory: str, k: int = 0) -> Dict[str, List[Set[str]]]:
    """Read all ranked lists from a directory."""
    path = Path(directory)
    d = {}
    for f in path.iterdir():
        d[f.stem] = read_list(f, k)
    return d


if __name__ == '__main__':
    args = get_arguments()

    vd = get_lists(args.virus_dir, args.k)
    hd = get_lists(args.host_dir, args.k)

    vnames = sorted(vd)
    hnames = sorted(hd)

    # Filter down the number of pairs
    vds = []
    for i, vname in enumerate(vnames):
        vs = set()
        for rset in vd[vname]:
            for item in rset:
                vs.add(item)
        vds.append(vs)

    q = []
    for hi, hname in enumerate(hnames):
        hs = set([item for rset in hd[hname] for item in rset])
        for vi, vs in enumerate(vds):
            if vs.intersection(hs):
                q.append((hi, vi, args.p))

    # Calculate RBO scores between every phage and every host.
    data = np.zeros((len(hnames), len(vnames)))
    with multiprocessing.Pool(args.num_threads) as pool:
        res = pool.starmap(rbo_wrap, q)
        for hi, vi, score in res:
            data[hi, vi] = score

    # Save matrix to file.
    df = pd.DataFrame(data=data, index=hnames, columns=vnames)
    df.to_csv(f'{args.out.name}.matrix.csv')

    # For each phage find host with the highest score.
    args.out.write(f'phage,host,score\n')
    for vname in vnames:
        max_score = df[vname].max()
        host_names = df.loc[df[vname] == max_score].index
        for hname in host_names:
            args.out.write(f'{vname},{hname},{max_score}\n')
    args.out.close()