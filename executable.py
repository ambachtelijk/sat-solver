import os
import sys


splits = {'-S1': 'fifo', '-S2': 'dlcs__reversed', '-S3': 'dlis__reversed'}
if sys.argv[1] not in splits:
    print("Value of first argument is '{}', '-S1' '-S2' or '-S3' expected.".format(sys.argv[1]))
elif not os.path.exists(sys.argv[2]):
    print("File from second argument does not exist: '{}'".format(sys.argv[2]))
else:
    split = splits[sys.argv[1]]
    problem_filename = sys.argv[2]
