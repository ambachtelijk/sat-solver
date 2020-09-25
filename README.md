# SAT solver
Install the [Sympy library](https://docs.sympy.org)
`pip install -r requirements.txt`


To encode from Sudoku to DIMACS format, use the `sudoku-to-dimacs.py` tool. 

`py tools\sudoku_to_dimacs.py input\sudoku\n-open.txt input\rules\sudoku-rules-9x9.txt input\dimacs\n-open`

`py tools\sudoku_to_dimacs.py input\sudoku\n-freq.txt input\rules\sudoku-rules-9x9.txt input\dimacs\n-freq`

## Run experiments
To run the experiments, use the `experiments.py` script. This script will only write out benchmarks in CSV format. 
It will not store Sudoku solutions, these are only printed.

`experiments.py <prefix_input> <prefix_output> <splits> <n> <offset>`

Possible values for splits are:
fifo, fifo__reversed, fifo__negative_only, fifo__positive_only,
dlcs, dlcs__reversed, dlcs__negative_only, dlcs__positive_only,
dlis, dlis__reversed, dlis__negative_only, dlis__positive_only,
mfld, mfld__reversed, mfld__negative_only, mfld__positive_only,

### Experiment 1
`experiments.py input\dimacs\n-open output\experiment1 fifo__positive_only,dlcs__positive_only,dlis__positive_only,mfld__positive_only 100 0`


### Experiment 2
`experiments.py input\dimacs\n-freq output\experiment2 fifo__positive_only,mfld__positive_only 25 0`
