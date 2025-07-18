import subprocess
from google.genai import types

def git_commit_push(working_directory, message):
    try:
        # Stage all changes
        subprocess.run(["git", "add", "."], cwd=working_directory, check=True)
        # Commit with the provided message
        subprocess.run(["git", "commit", "-m", message], cwd=working_directory, check=True)
        # Push to main branch
        subprocess.run(["git", "push", "origin", "main"], cwd=working_directory, check=True)
        return "Successfully committed and pushed all changes to the main branch."
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {str(e)}"

schema_git_commit_push = types.FunctionDeclaration(
    name="git_commit_push",
    description="Stages all changes, commits with a message, and pushes to the main branch.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "message": types.Schema(
                type=types.Type.STRING,
                description="The commit message to use.",
            ),
        },
    ),
) 