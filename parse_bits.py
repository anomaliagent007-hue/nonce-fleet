#!/usr/bin/env python3
import sys, os, re
from pathlib import Path

def parse_v_lines(out_file):
    """Parse DIMACS v-lines from cadical/kissat output."""
    bits = []
    with open(out_file, 'r') as f:
        for line in f:
            if line.startswith('v '):
                tokens = line.strip().split()[1:]  # skip 'v'
                for token in tokens:
                    if token == '0':
                        break  # end of assignment
                    try:
                        n = int(token)
                        if n > 0:
                            bits.append('1')
                        else:
                            bits.append('0')
                    except ValueError:
                        pass
    return ''.join(bits)

def parse_nonceflow(out_file):
    """Parse nonceflow bits file."""
    try:
        with open(out_file, 'rb') as f:
            content = f.read()
        # should be ASCII 0/1
        return ''.join(c for c in content.decode('ascii', 'ignore') if c in '01')
    except:
        return None

def parse_fps(out_file):
    """Try to parse FPS output for assignment."""
    # FPS saves best assignment to a file? Check fps.c output.
    # For now, assume no bits output → return None
    return None

def main():
    out_file = sys.argv[1]
    solver = sys.argv[2] if len(sys.argv) > 2 else 'unknown'
    
    bits = None
    if solver in ['cadical', 'kissat']:
        bits = parse_v_lines(out_file)
    elif solver == 'nonceflow':
        bits = parse_nonceflow(out_file)
    elif solver == 'fps':
        bits = parse_fps(out_file)
    
    if bits and len(bits) > 0:
        # Verify if we know the expected length
        if solver == 'nonceflow':
            # Check for SATISFIABLE in out_file
            with open(out_file, 'r') as f:
                if 'SATISFIABLE' not in f.read():
                    print("NO_SOLUTION")
                    exit(0)
        print(bits)
        exit(0)
    else:
        print("NO_SOLUTION")
        exit(1)

if __name__ == '__main__':
    main()