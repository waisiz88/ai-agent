import os  # For environment variables
import sys  # For command line arguments
from dotenv import load_dotenv  # For loading .env file
from google import genai  # For Gemini API
from google.genai import types  # Import types for Content and Part classes
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file import write_file_secure, schema_write_file

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

load_dotenv()  # Load environment variables from .env

api_key = os.getenv("GEMINI_API_KEY")  # Get API key from environment
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

# Check for --verbose flag and remove it from the arguments if present
verbose = False
args = sys.argv[1:]  # All arguments after the script name
if "--verbose" in args:
    verbose = True
    args.remove("--verbose")  # Remove the flag so it doesn't become part of the prompt

if not args:  # If no prompt is provided
    print("Error: Please provide a prompt as a command line argument.")
    sys.exit(1)

prompt = " ".join(args)  # Join the remaining arguments to form the prompt

client = genai.Client(api_key=api_key)  # Create Gemini API client

# Create a list of messages for the conversation, with the user's prompt as the only message
messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),  # The user's message
]

# Create the available_functions Tool
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

# Create the config with tools and system_instruction
config = types.GenerateContentConfig(
    tools=[available_functions],
    system_instruction=system_prompt
)

# Function dispatcher for tool calls
def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = dict(function_call_part.args)
    args["working_directory"] = "calculator"  # Always inject working directory
    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")
    # Map function names to actual functions
    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file_secure,
    }
    func = function_map.get(function_name)
    if not func:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    # Actually call the function
    try:
        function_result = func(**args)
    except Exception as e:
        function_result = f"Error: {str(e)}"
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

max_iterations = 20
iteration = 0

try:
    while iteration < max_iterations:
        iteration += 1
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=config,
        )
        # Add all candidate contents to the messages list
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    messages.append(candidate.content)
        # Check for function calls in the response
        if hasattr(response, 'function_calls') and response.function_calls:
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose=verbose)
                # Check for function response in the result
                if not (function_call_result.parts and hasattr(function_call_result.parts[0], "function_response") and hasattr(function_call_result.parts[0].function_response, "response")):
                    raise RuntimeError("Fatal: No function response in tool call result.")
                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
                # Add the tool response to the messages list
                messages.append(function_call_result)
            # Continue the loop for the next step
            continue
        # If we get a text response, print and break
        if hasattr(response, 'text') and response.text:
            print(response.text)
            break
        # If nothing else, break to avoid infinite loop
        break
except Exception as e:
    print(f"Error during agent loop: {e}")

# Get the usage metadata from the response (contains token counts)
usage = response.usage_metadata

# If verbose, print extra information
if verbose:
    print(f'User prompt: {prompt}')
    if usage is not None:
        print(f"Prompt tokens: {usage.prompt_token_count}")
        print(f"Response tokens: {usage.candidates_token_count}")
