from functions.run_python import run_python_file

if __name__ == "__main__":
    print(run_python_file("calculator", "main.py"))
    print()

    print(run_python_file("calculator", "main.py", ["3 + 5"]))
    print()

    print(run_python_file("calculator", "../main.py"))
    print()

    print(run_python_file("calculator", "nonexistent.py"))
    print() 