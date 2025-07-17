import os
from functions.config import MAX_FILE_CHARACTERS

def read_file_secure(working_directory, file_path):
    try:
        # Join and resolve the full path
        full_path = os.path.join(working_directory, file_path)
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(full_path)

        # Check if the file is within the working directory
        if not abs_file_path.startswith(abs_working_dir):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Read the file contents
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Truncate if necessary
        if len(content) > MAX_FILE_CHARACTERS:
            truncated_content = content[:MAX_FILE_CHARACTERS]
            truncated_content += f'\n[...File "{file_path}" truncated at {MAX_FILE_CHARACTERS} characters]'
            return truncated_content
        else:
            return content

    except Exception as e:
        return f'Error: {str(e)}'
