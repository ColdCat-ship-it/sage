from sage.all import *
import random
import math
import sys
import csv
import time

# --- Configuration ---
print("----running----")

R = PolynomialRing(QQ, 'x')
x = R.gen()
a = 489
b = 170
N = max(4 * b, a)
F = (
        x ** (4 * b + N) - x**(2 * b + N) - x**(a + N) - 2 * x**N
        - x**(N - a) - x**(N - 2 * b) + x**(N - 4 * b)
        )
factors = F.factor()
for factor, multiplicity in factors:
    print(f"Factor: {factor}, Multiplicity: {multiplicity}")
print(f"Total number of factors: {len(factors)}")
# Output the degrees of the factors
degrees = [factor.degree() for factor, multiplicity in factors]
print(f"Degrees of factors: {degrees}")