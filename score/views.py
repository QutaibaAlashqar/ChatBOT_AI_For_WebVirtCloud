import json
import os
import subprocess
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# A dictionary to keep track of subprocesses and commands
processes = {}
commands = {}

# Define the FLAG_FILE path
FLAG_FILE = '/tmp/llama_ready.flag'  # Update this path as necessary

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def chat_with_bot(request):
    if request.method == 'POST':
        print("Received POST request.")
        if not os.path.exists(FLAG_FILE):
            print("Llama model is not ready.")
            return JsonResponse({'message': 'Llama model is not ready yet. Please wait.'})

        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        print(f"User message: {user_message}")

        try:
            # Generate a unique session ID (or use a better unique identifier)
            session_id = request.session.session_key or str(uuid.uuid4())

            # If a process exists for this session, use it; otherwise, create a new one
            if session_id in processes:
                process = processes[session_id]
            else:
                command = [
                    '/home/ozgur-ent/Desktop/ChatBotAI/open-interpreter/venv39/bin/interpreter',
                    '--local', '--llama3'
                ]
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                processes[session_id] = process

            # Send the user message to the process
            stdout, stderr = process.communicate(input=user_message, timeout=3000)

            # Filter out unwanted text
            filtered_output = filter_output(stdout)

            if stderr:
                print(f"Subprocess stderr: {stderr.strip()}")  # Debug line

            bot_message = filtered_output.strip() or "No output from interpreter."
            print(f"Bot message: {bot_message}")

            # Check if bot message contains the question
            if "Would you like to run this code? (y/n)" in bot_message:
                # Extract the command from the bot message
                command_to_run = extract_command_from_message(bot_message)
                commands[session_id] = command_to_run  # Store the command for this session
                return JsonResponse({'message': bot_message, 'run_code_prompt': True, 'session_id': session_id})

            return JsonResponse({'message': bot_message})

        except FileNotFoundError:
            print("Error: Interpreter executable not found.")
            return JsonResponse({'message': "Error: Interpreter executable not found."})
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({'message': f"Unexpected error: {str(e)}"})

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def handle_code_execution(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_choice = data.get('choice')
        session_id = data.get('session_id')

        if user_choice == 'y':
            if session_id in commands:
                command_to_run = commands.pop(session_id)
                
                # Log the command being executed
                print(f"Attempting to execute command: {command_to_run}")

                try:
                    result = subprocess.run(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True, shell=True)
                    output = result.stdout
                    error = result.stderr
                    if error:
                        print(f"Subprocess stderr: {error.strip()}")
                    bot_message = output.strip() or "No output from command."
                    print(f"Bot message: {bot_message}")
                    return JsonResponse({'message': bot_message})
                except subprocess.CalledProcessError as e:
                    print(f"CalledProcessError: {str(e)}")
                    return JsonResponse({'message': f"Error executing command: {str(e)}"}, status=500)
                except Exception as e:
                    print(f'Unexpected error: {str(e)}')
                    return JsonResponse({'message': f'Unexpected error: {str(e)}'}, status=500)
            else:
                return JsonResponse({'message': 'No command found for this session.'}, status=400)
        
        elif user_choice == 'n':
            return cancel_process(request)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def cancel_process(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')

            if session_id in processes:
                process = processes[session_id]
                process.terminate()
                process.wait()
                del processes[session_id]
                return JsonResponse({'message': 'Process terminated successfully.'})
            else:
                return JsonResponse({'message': 'No process found to terminate.'})

        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'})

def filter_output(output):
    """
    Filter out unwanted text from the interpreter output.
    Collects lines only after the '>' line.
    """
    lines = output.splitlines()
    filtered_lines = []
    is_output_section = False

    for line in lines:
        # Start collecting output lines after the '>' line
        if is_output_section:
            filtered_lines.append(line)
        if line.strip() == ">":
            is_output_section = True

    return "\n".join(filtered_lines)



def extract_command_from_message(message):
    """
    Extract the command from the bot's message.
    Assumes the command is included in the message and is directly before the prompt.
    """
    lines = message.splitlines()
    command_lines = []
    prompt_found = False

    # Traverse the lines in reverse order to find the prompt first and then collect command lines
    for line in reversed(lines):
        if 'Would you like to run this code? (y/n)' in line:
            prompt_found = True
        elif prompt_found:
            stripped_line = line.strip()
            if stripped_line:
                command_lines.append(stripped_line)
            else:
                if command_lines:
                    break

    # Since we traversed in reverse, reverse command_lines to get the correct order
    command_lines.reverse()

    # Join the command lines and strip leading/trailing whitespace
    command = "\n".join(command_lines).strip()
    return command
