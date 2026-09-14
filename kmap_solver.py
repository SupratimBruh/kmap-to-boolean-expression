import sys
import math

def get_gray_code(bits):
    """Generates the standard Gray code sequence for a given number of bits."""
    if bits == 0: return [0]
    g = [0, 1]
    for i in range(2, bits + 1):
        # Reflect and add the 1-bit in the new position
        g = g + [x + (1 << (i - 1)) for x in reversed(g)]
    return g

def covers(pi, minterm):
    """Checks if a prime implicant covers a given minterm."""
    for p, m in zip(pi, minterm):
        if p != '-' and p != m:
            return False
    return True

def get_prime_implicants(minterm_strs, n):
    """Quine-McCluskey Step 1: Find all Prime Implicants."""
    groups = {}
    # Group minterms by the number of 1s they contain
    for s in minterm_strs:
        c = s.count('1')
        if c not in groups: groups[c] = set()
        groups[c].add(s)

    prime_implicants = set()
    while groups:
        new_groups = {}
        marked = set()
        group_keys = sorted(list(groups.keys()))
        
        # Compare adjacent groups
        for i in range(len(group_keys)):
            k1 = group_keys[i]
            k2 = k1 + 1
            if k2 in groups:
                for s1 in groups[k1]:
                    for s2 in groups[k2]:
                        # Count bit differences (Hamming distance)
                        diff = 0
                        diff_idx = -1
                        for idx in range(n):
                            if s1[idx] != s2[idx]:
                                diff += 1
                                diff_idx = idx
                        
                        # If they differ by exactly 1 bit, combine them
                        if diff == 1:
                            marked.add(s1)
                            marked.add(s2)
                            new_s = s1[:diff_idx] + '-' + s1[diff_idx+1:]
                            new_c = new_s.count('1')
                            if new_c not in new_groups:
                                new_groups[new_c] = set()
                            new_groups[new_c].add(new_s)

        # Unmarked terms become prime implicants
        for k in groups:
            for s in groups[k]:
                if s not in marked:
                    prime_implicants.add(s)
        groups = new_groups
        
    return list(prime_implicants)

def pi_to_str(pi):
    """Converts a binary/dash string to a boolean variable string."""
    vars = ['a', 'b', 'c', 'd', 'e']
    res = []
    for i, char in enumerate(pi):
        if char == '1':
            res.append(vars[i])
        elif char == '0':
            res.append(vars[i] + "'")
    return "".join(res)

def solve(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    # Parse matrix
    matrix = []
    for line in lines:
        row = [int(x) for x in line.strip().split() if x in ('0', '1')]
        if row:
            matrix.append(row)

    if not matrix:
        print("Empty matrix")
        return

    R = len(matrix)
    C = len(matrix[0])
    n = int(math.log2(R * C))
    r_bits = int(math.log2(R))
    c_bits = int(math.log2(C))

    # K-Map coordinates map directly to Gray code
    row_map = get_gray_code(r_bits)
    col_map = get_gray_code(c_bits)

    # 1. Translate matrix into minterms
    minterms = []
    for i in range(R):
        for j in range(C):
            if matrix[i][j] == 1:
                # Columns act as MSB (a, b), Rows act as LSB (c, d)
                m = (col_map[j] << r_bits) | row_map[i]
                minterms.append(m)

    if not minterms:
        print("0")
        return
    if len(minterms) == R * C:
        print("1")
        return

    minterm_strs = [format(m, f'0{n}b') for m in minterms]

    # 2. Get Prime Implicants
    pis = get_prime_implicants(minterm_strs, n)

    # 3. Build Prime Implicant Coverage Chart
    minterm_covered_by = {m: [] for m in minterm_strs}
    for i, pi in enumerate(pis):
        for m in minterm_strs:
            if covers(pi, m):
                minterm_covered_by[m].append(i)

    # 4. Petrick's Method (POS to SOP expansion)
    expressions = [minterm_covered_by[m] for m in minterm_strs]
    sop = [set([idx]) for idx in expressions[0]]
    
    for i in range(1, len(expressions)):
        current_sum = [set([idx]) for idx in expressions[i]]
        next_sop = []
        for t1 in sop:
            for t2 in current_sum:
                next_sop.append(t1.union(t2))
        
        # Apply Boolean Absorption Law (A + AB = A)
        filtered_sop = []
        next_sop.sort(key=len) # Process shortest term first
        for term in next_sop:
            # If no subset exists in our filtered list, it's a new minimal term
            if not any(existing.issubset(term) for existing in filtered_sop):
                filtered_sop.append(term)
        sop = filtered_sop

    # 5. Extract minimal covers
    min_pi_count = min(len(cover) for cover in sop)
    min_pi_covers = [cover for cover in sop if len(cover) == min_pi_count]

    def cost(cover):
        return sum(n - pis[idx].count('-') for idx in cover)

    min_cost = min(cost(cover) for cover in min_pi_covers)
    final_covers = [cover for cover in min_pi_covers if cost(cover) == min_cost]

    # Format the output strings
    final_strings = []
    for cover in final_covers:
        terms = sorted([pi_to_str(pis[idx]) for idx in cover])
        final_strings.append(" + ".join(terms))

    # Print all minimal expressions alphabetically
    final_strings.sort()
    for expr in final_strings:
        print(expr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kmap_solver.py <filename>")
    else:
        solve(sys.argv[1])