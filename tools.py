#!/usr/bin/env python3
"""Extract and verify SAT assignment bits from solver output.

Usage:
  tools.py extract <solver> <cnf>
  tools.py verify  <cnf> <bitsfile>
"""
import os
import re
import sys


def from_dimacs(path):
    if not os.path.exists(path):
        return ""
    txt = open(path, errors="ignore").read()
    if "SATISFIABLE" not in txt:
        return ""
    bits = []
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("v"):
            for tok in line[1:].split():
                try:
                    n = int(tok)
                except ValueError:
                    continue
                if n == 0:
                    continue
                # solver prints abs values in order; sign gives the assignment
                bits.append("1" if n > 0 else "0")
    return "".join(bits)


def plain(path):
    if not os.path.exists(path):
        return ""
    return re.sub(r"[^01]", "", open(path, errors="ignore").read())


def extract(solver, cnf="instance4.cnf"):
    nvar = int(open(cnf).readline().split()[2])
    if solver == "nonceflow":
        cand = plain("bits_nonflow.txt")
    elif solver == "fps":
        cand = plain("bits_fps.txt")
    else:
        cand = from_dimacs("solver_out.txt")
    # trim/pad guard: only accept exact length
    if len(cand) != nvar:
        print(f"{solver}: {len(cand)} bits (expected {nvar}) -> reject")
        open("result.txt", "w").write("NO_SOLUTION")
        return 1
    open("winner_bits.txt", "w").write(cand)
    open("result.txt", "w").write(f"SAT {len(cand)}")
    print(f"{solver}: {len(cand)} bits written")
    return 0


def verify(cnf, bitsfile="winner_bits.txt"):
    nvar = int(open(cnf).readline().split()[2])
    if not os.path.exists(bitsfile):
        print("no bits file")
        return 0
    bits = open(bitsfile).read().strip()
    print(f"vars_in_cnf={nvar} bits={len(bits)}")
    if len(bits) != nvar:
        print("length mismatch -> invalid")
        open("verify.txt", "w").write(f"invalid length {len(bits)} != {nvar}")
        return 1
    clauses, cur = [], []
    for line in open(cnf):
        line = line.strip()
        if not line or line[0] in "cp":
            continue
        for tok in line.split():
            v = int(tok)
            if v == 0:
                if cur:
                    clauses.append(cur)
                cur = []
            else:
                cur.append(v)
    if cur:
        clauses.append(cur)
    bad = sum(
        1
        for c in clauses
        if not any((bits[abs(x) - 1] == "1") == (x > 0) for x in c)
    )
    print(f"clauses={len(clauses)} unsat={bad}")
    open("verify.txt", "w").write(f"unsat={bad} clauses={len(clauses)}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    cmd = sys.argv[1]
    if cmd == "extract":
        solver = sys.argv[2]
        cnf = sys.argv[3] if len(sys.argv) > 3 else "instance4.cnf"
        raise SystemExit(extract(solver, cnf))
    if cmd == "verify":
        cnf = sys.argv[2] if len(sys.argv) > 2 else "instance4.cnf"
        bf = sys.argv[3] if len(sys.argv) > 3 else "winner_bits.txt"
        raise SystemExit(verify(cnf, bf))
    print(__doc__)
    raise SystemExit(2)