import sys
import subprocess
from compiler import compile_to_c

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 samlang.py file.sam")
        return

    sam_file = sys.argv[1]

    with open(sam_file, "r") as f:
        code = f.read()

    c_code = compile_to_c(code)

    with open("output.c", "w") as f:
        f.write(c_code)

    print("C code generated: output.c")

    # Compile
    compile_process = subprocess.run(["gcc", "output.c", "-o", "output"])

    if compile_process.returncode != 0:
        print("Compilation failed")
        return

    print("\nRunning program:\n")

    subprocess.run(["./output"])

if __name__ == "__main__":
    main()