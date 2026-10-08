#!/usr/bin/env python3
"""Module launcher; shared implementation in vinyl_suite.py."""
import sys
from vinyl_suite import main

if __name__ == '__main__':
    args=sys.argv[1:]
    global_args=[]
    if '--state' in args:
        pos=args.index('--state')
        if pos+1>=len(args): raise SystemExit('--state needs a path')
        global_args=args[pos:pos+2]; del args[pos:pos+2]
    sys.argv=[sys.argv[0],*global_args,'export',*args]
    try: main()
    except (ValueError,KeyError,FileNotFoundError,FileExistsError) as e:
        print('ERROR:',e); raise SystemExit(2)
