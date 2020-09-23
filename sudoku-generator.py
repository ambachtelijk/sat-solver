from random import sample
from itertools import repeat

base  = 3
side  = 9

# pattern for a baseline valid solution
def pattern(r,c):
    return (base*(r%base)+r//base+c)%side

def shuffle(s):
    return sample(s,len(s))

rBase = range(base)
rows  = [g*base + r for g in shuffle(rBase) for r in shuffle(rBase)]
cols  = [g*base + c for g in shuffle(rBase) for c in shuffle(rBase)]
nums  = shuffle(range(1,10))

# produce board using randomized baseline pattern
sudo = [ [nums[pattern(r,c)] for c in cols] for r in rows ]

squares = side*side
empties = squares * 64//81
for p in sample(range(squares),empties):
    sudo[p//side][p%side] = 0

numSize = len(str(side))

for line in sudo: print("".join(f"{n or '.':{numSize}}" for n in line))