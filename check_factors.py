from sage.all import *
import csv
import sys

# --- Settings ---
B_RANGE = range(1, 201)   # b = 1 to 200
A_RANGE = range(1, 1001)  # a = 1 to 1000
CSV_FILENAME = 'raw_results.csv'
SUMMARY_FILENAME = 'summary_by_b.txt'

def is_symmetric(poly):
    if poly == 0: return True
    coeffs = poly.list()
    return coeffs == coeffs[::-1]

def solve_case(a, b):
    R = PolynomialRing(GF(2), 'x')
    x = R.gen()

    # 1. Define Exponents & Normalize
    # Offsets: 4b, 2b, a, -a, -2b, -4b. Shifted so min is 0.
    raw_exponents = [8*b, 6*b, 4*b + a, 4*b - a, 2*b, 0]
    min_exp = min(raw_exponents)
    shifted_exponents = [e - min_exp for e in raw_exponents]
    
    F = sum(x**e for e in shifted_exponents)

    # 2. Divisors
    g = x + 1
    k = x**2 + x + 1
    fac = F
    
    # 3. Reductions
    if a % 2 == 1:
        if fac % (g**2) == 0: fac = fac // (g**2)
    if a % 3 == 0:
        if fac % k == 0: fac = fac // k

    # 4. Factorize & Analyze
    factored_obj = factor(fac)
    sym_count = 0
    asym_count = 0
    
    for poly_factor, exponent in factored_obj:
        if is_symmetric(poly_factor):
            sym_count += 1
        else:
            asym_count += 1
            
    if asym_count == 0: return 1      # All Symmetric
    elif sym_count > 0: return 2      # Mixed
    else: return 3                    # All Asymmetric

# --- Main Execution ---

# Open files for writing
with open(CSV_FILENAME, 'w', newline='') as csvfile, \
     open(SUMMARY_FILENAME, 'w') as sumfile:

    # Setup CSV Writer
    writer = csv.writer(csvfile)
    writer.writerow(['b', 'a', 'case']) # Header

    # Write Header to Summary File
    sumfile.write(f"{'b':<5} | {'Case 1 (Sym)':<12} {'Case 2 (Mix)':<12} {'Case 3 (Asym)':<12} | {'Total Valid a'}\n")
    sumfile.write("-" * 65 + "\n")

    print(f"Starting run. Raw data -> {CSV_FILENAME}, Summary -> {SUMMARY_FILENAME}")

    for b in B_RANGE:
        # Counters for this specific b
        stats = {1: 0, 2: 0, 3: 0}
        total_valid_a = 0
        
        # Progress output to terminal (stderr)
        sys.stderr.write(f"\rProcessing b={b}...")

        for a in A_RANGE:
            if gcd(a, b) == 1:
                try:
                    case_num = solve_case(a, b)
                    
                    # 1. Write specific result to CSV immediately
                    writer.writerow([b, a, case_num])
                    
                    # 2. Update stats for this b
                    stats[case_num] += 1
                    total_valid_a += 1
                    
                except Exception as e:
                    # Log error in CSV as Case -1
                    writer.writerow([b, a, -1])

        # End of loop for 'a'. Write the summary for this 'b' to text file.
        summary_line = (
            f"{b:<5} | "
            f"{stats[1]:<12} "
            f"{stats[2]:<12} "
            f"{stats[3]:<12} | "
            f"{total_valid_a}"
        )
        
        sumfile.write(summary_line + "\n")
        
        # Flush buffers so data is saved even if Codespace crashes
        csvfile.flush()
        sumfile.flush()

sys.stderr.write("\nDone.\n")