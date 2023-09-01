import random
from typing import Optional


# todo: intじゃなくてstrで来るんだよな
def gen_seeds(n: Optional[int] = 100, seed: Optional[int] = 42, upper_bound: Optional[int] = 2**64 - 1):
    n = int(n) if n is not None and n != 0 else 100
    upper_bound = int(upper_bound) if upper_bound is not None else 2**64 - 1

    if seed is not None:
        random.seed(seed)

    for i in range(n):
        print(random.randint(0, upper_bound))
