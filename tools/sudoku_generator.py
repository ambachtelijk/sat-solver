from random import sample

distributions = [
    [0, 0, 0, 0, 0, 1, 1, 1, 9],
    [0, 0, 0, 0, 0, 1, 1, 2, 8],
    [0, 0, 0, 0, 1, 1, 1, 2, 7],
    [0, 0, 0, 0, 1, 1, 2, 2, 6],
    [0, 0, 0, 1, 1, 1, 2, 2, 5],
    [0, 0, 1, 1, 1, 1, 2, 2, 4],
    [0, 1, 1, 1, 1, 2, 2, 2, 3]
]

base = 3
side = 9


# pattern for a baseline valid solution
def pattern(r, c):
    return (base * (r % base) + r // base + c) % side


def shuffle(s):
    return sample(s, len(s))


def generate_sudoku():
    r_base = range(base)
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, 10))

    # produce board using randomized baseline pattern
    return [nums[pattern(r, c)] for c in cols for r in rows]


for distribution in distributions:
    for k in range(0, 100):
        sudoku = generate_sudoku()
        for i, freq in enumerate(distribution):
            positions = sample(range(1, 10), freq)
            current_pos = 0
            for j, value in enumerate(sudoku):
                if value == i + 1:
                    current_pos += 1
                    if current_pos not in positions:
                        sudoku[j] = 0

        print("".join(f"{n or '.':{1}}" for n in sudoku))
