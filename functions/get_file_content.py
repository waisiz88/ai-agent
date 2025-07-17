import os
from google.genai import types

def get_file_content(working_directory, file_path):
    try:
        # Join and resolve the full path
        full_path = os.path.join(working_directory, file_path)
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(full_path)

        # Check if the file is within the working directory
        if not abs_file_path.startswith(abs_working_dir):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Now you can safely read the file (add your file reading logic here)
        with open(abs_file_path, 'r') as f:
            return f.read()

    except Exception as e:
        return f'Error: {str(e)}'

# Function declaration for getting file content
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of a file, constrained to the working directory. Truncates output if the file is too large.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
    ),
)