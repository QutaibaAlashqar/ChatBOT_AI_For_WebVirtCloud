import json
import os
import subprocess
import signal
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

FLAG_FILE = '/tmp/llama_ready.flag'
PID_FILE = '/tmp/interpreter_pid.txt'

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
            # Command to start the interpreter process
            command = [
                '/home/ozgur-ent/Desktop/ChatBotAI/open-interpreter/venv39/bin/interpreter',
                '--local', '--llama3'
            ]

            # Open the interpreter process
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Save the PID to a file
            with open(PID_FILE, 'w') as f:
                f.write(str(process.pid))

            try:
                # Send the user message and close stdin
                stdout, stderr = process.communicate(input=user_message, timeout=1000)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return JsonResponse({'message': "Error: Request timed out."})

            # Filter out unwanted text
            filtered_output = filter_output(stdout)

            if stderr:
                print(f"Subprocess stderr: {stderr.strip()}")  # Debug line

            bot_message = filtered_output.strip() or "No output from interpreter."
            print(f"Bot message: {bot_message}")
            return JsonResponse({'message': bot_message})

        except FileNotFoundError:
            print("Error: Interpreter executable not found.")
            return JsonResponse({'message': "Error: Interpreter executable not found."})
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({'message': f"Unexpected error: {str(e)}"})

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def cancel_process(request):
    if request.method == 'POST':
        try:
            # Read the PID from the file
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())

            # Terminate the process
            os.kill(pid, signal.SIGINT)

            # Remove the PID file
            os.remove(PID_FILE)

            return JsonResponse({'message': 'Process terminated successfully.'})

        except FileNotFoundError:
            return JsonResponse({'message': 'No process found to terminate.'})
        except ProcessLookupError:
            return JsonResponse({'message': 'Process not found.'})
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
