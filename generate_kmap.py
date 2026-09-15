import random
import sys

def generate_kmap(filename="input.txt", n=None):
    if n is None:
        n = random.randint(1, 5)
    elif not (1 <= n <= 5):
        print("Error: Number of variables n must be between 1 and 5.")
        return

    r_bits = n // 2
    c_bits = n - r_bits
    R = 1 << r_bits
    C = 1 << c_bits

    matrix = [[random.choice([0, 1]) for _ in range(C)] for _ in range(R)]

    with open(filename, 'w') as f:
        for row in matrix:
            f.write(" ".join(map(str, row)) + "\n")

    print(f"Generated a {R}x{C} K-Map ({n} variables) in '{filename}'.")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    num_vars = int(sys.argv[2]) if len(sys.argv) > 2 else None
    generate_kmap(output_file, num_vars)