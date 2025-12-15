from sage.all import *
import random
import math
import sys
import csv
import time

# --- Configuration ---
# We sample 'b' such that log10(b) is between MIN_LOG and MAX_LOG.
# MAX_LOG = 4.5 implies b goes up to ~31,000 (Degree ~250,000).
# WARNING: Increasing MAX_LOG > 5.5 may cause Memory Errors or infinite runtimes.
MIN_LOG = 1.0
MAX_LOG = 4.5
NUM_SAMPLES = 1000  # How many random pairs to test overnight
CSV_FILENAME = 'conjecture_verification.csv'

def get_random_pair(min_log, max_log):
    """
    Generates a random (a, b) pair where:
    1. b is sampled from a logarithmic distribution.
    2. a is random, a < 4b.
    3. a is ODD.
    4. gcd(a, b) == 1.
    """
    while True:
        # 1. Sample b logarithmically
        exponent = random.uniform(min_log, max_log)
        b = int(10**exponent)
        if b < 1: b = 1
        
        # 2. Sample a (approx same magnitude or smaller, let's say up to 4b)
        # We want 'a' to be odd.
        a = random.randint(1, 4 * b)
        if a % 2 == 0:
            a += 1
            
        if gcd(a, b) == 1:
            return a, b

def check_conjecture(a, b):
    R = PolynomialRing(QQ, 'x')
    x = R.gen()

    N = max(4 * b, a)
    # Construct Polynomial F
    F = (
        x ** (4 * b + N) - x**(2 * b + N) - x**(a + N) - 2 * x**N
        - x**(N - a) - x**(N - 2 * b) + x**(N - 4 * b)
        )
    # 1. Construct Polynomial F
    # Offsets: 4b, 2b, a, -a, -2b, -4b. Normalized to start at 0.
    # Exponents: 8b, 6b, 4b+a, 4b-a, 2b, 0
    # raw_exponents = [8*b, 6*b, 4*b + a, 4*b - a, 2*b, 0]
    # # min_exp = min(raw_exponents)
    # # shifted_exponents = [e - min_exp for e in raw_exponents]
    # F = sum(x**e for e in raw_exponents)

    # 2. Define Divisors
    g = x + 1
    k = x**2 - x + 1 # This is (x^2 - x + 1) in GF(2)
    
    # 3. Apply Reduction Logic (The Conjecture)
    # Conjecture part 1: Always divide by (x+1)^2 if a is odd (which it is)
    if F % (g**2) != 0:
        return "ERROR_DIV_G", False
    
    reduced_F = F // (g**2)
    
    # Conjecture part 2: If a % 3 == 0, divide by k
    expected_div_by_k = (a % 3 == 0)
    
    if expected_div_by_k:
        if reduced_F % k != 0:
            return "ERROR_DIV_K", False
        reduced_F = reduced_F // k
    
    # 4. Check Irreducibility
    # is_irreducible() is very fast in Sage for GF(2)
    is_irr = reduced_F.is_irreducible()
    
    return "OK", is_irr

# --- Main Execution ---

print(f"Starting Random Monte Carlo Test.")
print(f"Range: 10^{MIN_LOG} to 10^{MAX_LOG} (Logarithmic scale)")
print(f"Target Samples: {NUM_SAMPLES}")
print("-" * 60)

with open(CSV_FILENAME, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['timestamp', 'b', 'a', 'log10_b', 'div_by_3', 'status', 'is_irreducible'])
    
    success_count = 0
    fail_count = 0
    
    start_time = time.time()

    for i in range(NUM_SAMPLES):
        a, b = get_random_pair(MIN_LOG, MAX_LOG)
        
        # Logging to stderr for progress monitoring
        sys.stderr.write(f"\rSample {i+1}/{NUM_SAMPLES} | Testing a={a}, b={b}...")
        
        try:
            status, result = check_conjecture(a, b)
            
            # Record Data
            writer.writerow([
                time.strftime("%H:%M:%S"),
                b, 
                a, 
                round(math.log10(b), 2),
                (a % 3 == 0),
                status,
                result
            ])
            csvfile.flush()
            
            if result is True:
                success_count += 1
            else:
                fail_count += 1
                # If valid math but NOT irreducible -> Counter Example Found!
                if status == "OK":
                    print(f"\n[COUNTER EXAMPLE FOUND] a={a}, b={b} is REDUCIBLE")
                    sys.exit(1)

        except Exception as e:
            writer.writerow([time.strftime("%H:%M:%S"), b, a, 0, False, "CRASH", str(e)])
            
sys.stderr.write("\nDone.\n")
print("-" * 60)
print(f"Total Tested: {NUM_SAMPLES}")
print(f"Consistent with Conjecture (Irreducible): {success_count}")
print(f"Counter Examples (Reducible): {fail_count}")
sys.exit(0)