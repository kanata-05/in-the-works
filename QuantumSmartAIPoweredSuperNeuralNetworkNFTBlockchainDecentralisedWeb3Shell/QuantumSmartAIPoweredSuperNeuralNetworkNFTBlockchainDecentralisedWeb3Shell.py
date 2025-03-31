import os
import dotenv
import subprocess
import sys
import google.generativeai as genai

dotenv.load_dotenv()

genai.configure(api_key=os.getenv("AI_API_key"))

generation_config = {
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 64,
    "response_mime_type": "text/plain",
}

shells = {
    "--bash": "bash", "--cmd": "cmd", "--powershell": "powershell", "--zsh": "zsh",
    "--bourne": "sh", "--ksh": "ksh", "--fish": "fish", "--korn": "ksh", "--tcsh": "tcsh"
}

shell_type = "powershell"  # Default shell
for arg in sys.argv[1:]:
    if arg in shells:
        shell_type = shells[arg]
        break

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

def get_command(user_request):
    prompt = f"Convert the following request into a {shell_type} command. Check if the command is safe, unless the query asks for such a command. Only return the command, no explanations or special symbols like backticks, just the plain command: {user_request}"
    response = model.generate_content(prompt)
    return response.text.strip("`")

def execute_command(command):
    if shell_type == "cmd":
        subprocess.run(["cmd", "/c", command], shell=True)
    else:
        subprocess.run([shell_type, "-c", command], shell=True)

def main():
    while True:
        user_input = input("QSAPSNNNFTBDWS> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        command = get_command(user_input)
        execute_command(command)

if __name__ == "__main__":
    main()
