import os
import sys
import json
import subprocess
import re
import google.generativeai as genai
from prompt_toolkit import prompt
from colorama import Fore, Style


GENAI_API_KEY = "AIzaSyCkDucG9x7LjPSiGCM5eKFnfdf9sU-zOno"
genai.configure(api_key=GENAI_API_KEY)


def get_command_from_ai(user_input):
    prompt_text = f'''
    User Input: "{user_input}"
    You are an AI that translates human language into system commands.
    Return ONLY a JSON object in the format:
    {{
        "command": "<system_command>",
        "description": "<brief explanation>"
    }}
    Do NOT return any other text or explanation.
    '''

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  
        response = model.generate_content(prompt_text)

        ai_response = response.text  
        print(Fore.YELLOW + "🔍 AI Raw Response:\n" + ai_response + Style.RESET_ALL)  

        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            try:
                command_data = json.loads(json_text)
                return command_data.get("command"), command_data.get("description")
            except json.JSONDecodeError:
                print(Fore.RED + " AI returned invalid JSON. Check response format." + Style.RESET_ALL)
                return None, None
        else:
            print(Fore.RED + " AI response does not contain valid JSON." + Style.RESET_ALL)
            return None, None

    except Exception as e:
        print(Fore.RED + f" Google Gemini API Error: {e}" + Style.RESET_ALL)
        return None, None


def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(Fore.CYAN + " Output:\n" + result.stdout + Style.RESET_ALL)
        if result.stderr:
            print(Fore.YELLOW + " Warning:\n" + result.stderr + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f" Error executing command: {e}" + Style.RESET_ALL)


def main():
    print(Fore.GREEN + " AI CLI - Type your command (or 'exit' to quit)" + Style.RESET_ALL)

    while True:
        user_input = prompt(" Enter Command: " )
        
        if user_input.lower() in ["exit", "quit"]:
            print(Fore.GREEN + " Goodbye!" + Style.RESET_ALL)
            break

        command, description = get_command_from_ai(user_input)

        if command:
            print(Fore.YELLOW + f" AI Interpretation: {description}" + Style.RESET_ALL)
            print(Fore.GREEN + f" Executing: {command}" + Style.RESET_ALL)
            execute_command(command)
        else:
            print(Fore.RED + " AI could not understand the command." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
