import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    try:
        # Join and resolve the full path
        full_path = os.path.join(working_directory, file_path)
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(full_path)

        # 1. Check if the file is within the working directory
        if not abs_file_path.startswith(abs_working_dir):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # 2. Check if the file exists
        if not os.path.isfile(abs_file_path):
            return f'Error: File "{file_path}" not found.'

        # 3. Check if the file is a Python file
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'

        # 4. Run the Python file with the provided arguments
        try:
            result = subprocess.run(
                ['python3', abs_file_path] + args,
                capture_output=True,
                text=True,
                cwd=abs_working_dir,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            return 'Error: executing Python file: Process timed out after 30 seconds.'
        except Exception as e:
            return f'Error: executing Python file: {e}'

        output_lines = []
        if result.stdout:
            output_lines.append(f'STDOUT:\n{result.stdout.strip()}')
        if result.stderr:
            output_lines.append(f'STDERR:\n{result.stderr.strip()}')
        if result.returncode != 0:
            output_lines.append(f'Process exited with code {result.returncode}')
        if not output_lines:
            return 'No output produced.'
        return '\n'.join(output_lines)

    except Exception as e:
        return f'Error: executing Python file: {e}'

# Function declaration for running a Python file
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="A list of arguments to pass to the Python file.",
            ),
        },
    ),
)