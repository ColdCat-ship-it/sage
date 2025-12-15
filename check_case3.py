from sage.all import *
import csv
import sys

# --- Settings ---
B_RANGE = range(1, 201)
A_RANGE = range(1, 1001)
CSV_FILENAME = 'pair_check_results.csv'

def is_symmetric(poly):
    if poly == 0: return True
    coeffs = poly.list()
    return coeffs == coeffs[::-1]

def are_reciprocals(p1, p2):
    """
    Checks if p1 and p2 are mirror images (reciprocals) of each other in GF(2).
    """
    c1 = p1.list()
    c2 = p2.list()
    # In GF(2), reciprocals mean the coefficient list is reversed
    return c1 == c2[::-1]

def analyze_factors(a, b):
    R = PolynomialRing(GF(2), 'x')
    x = R.gen()

    # 1. Construct & Normalize F
    raw_exponents = [8*b, 6*b, 4*b + a, 4*b - a, 2*b, 0]
    min_exp = min(raw_exponents)
    shifted_exponents = [e - min_exp for e in raw_exponents]
    F = sum(x**e for e in shifted_exponents)

    # 2. Reductions (Specific to your filter: a is odd, so divide g^2)
    # Note: We skip the check for a%2 or a%3 here because the main loop enforces it.
    g = x + 1
    fac = F // (g**2)

    # 3. Factorize
    factored_obj = factor(fac)
    
    # Flatten the factors into a simple list (handling multiplicity)
    # e.g., f^2 becomes [f, f]
    factors = []
    for p, exponent in factored_obj:
        for _ in range(exponent):
            factors.append(p)
    
    count = len(factors)
    
    # 4. Check if Case 3 (All Asymmetric)
    # If any factor is symmetric, it's not Case 3.
    for f in factors:
        if is_symmetric(f):
            return "Not Case 3", count, False

    # 5. Check "One Pair" Condition
    # We are looking for exactly 2 factors that are reciprocals
    is_recip_pair = False
    if count == 2:
        if are_reciprocals(factors[0], factors[1]):
            is_recip_pair = True
            
    return "Case 3", count, is_recip_pair

# --- Main Execution ---

with open(CSV_FILENAME, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Columns: b, a, Category, Factor Count, Is Perfect Pair?
    writer.writerow(['b', 'a', 'category', 'factor_count', 'is_reciprocal_pair'])
    
    print(f"Scanning for specific pairs in range b=[1,200]...")

    for b in B_RANGE:
        sys.stderr.write(f"\rProcessing b={b}...")
        
        for a in A_RANGE:
            # APPLY YOUR FILTER: a is odd AND not divisible by 3
            if (a % 2 == 1) and (a % 3 != 0) and (gcd(a, b) == 1):
                try:
                    category, count, is_pair = analyze_factors(a, b)
                    
                    # We only care to record it if it is Case 3 (All Asymmetric)
                    if category == "Case 3":
                        writer.writerow([b, a, category, count, is_pair])
                        
                        # If we find a Case 3 that is NOT a pair (count != 2), that's very interesting
                        if count != 2:
                            print(f"\n[Anomaly] b={b}, a={a}: Case 3 but has {count} factors!")
                        
                except Exception as e:
                    pass

sys.stderr.write("\nDone.\n")