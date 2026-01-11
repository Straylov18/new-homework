from random import randint
import math

def get_huge_random_number(seed1, seed2):
    output = 0
    for i in range(randint(seed1, seed2)):
        output += math.cos(i) * math.factorial(math.floor(41 + 40 * math.cos(i)))
    return output
