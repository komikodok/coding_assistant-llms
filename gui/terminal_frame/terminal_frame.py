import tkinter as tk
from tkinter import Scrollbar
import subprocess
import os

from threading import Thread
import re
from llms.llm_app import LLMApp


class TerminalFrame:
    def __init__(self, root, chatbot_frame):
        self.chatbot_frame = chatbot_frame
        self.llm_app = LLMApp()

        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(self.frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set, bg="black", fg="white")
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.bind('<Return>', self.execute_command)

        self.scrollbar.config(command=self.text.yview)

        self.insert_prompt()

    def insert_prompt(self):
        cwd = os.getcwd()
        self.text.insert(tk.END, f"{cwd}$ ")
        self.text.mark_set("insert", "end-1c")
        self.text.see(tk.END)

    def threading_llm(self, user_input):
        self.chatbot_frame.freeze_button_entry_while_threading() # Method from ChatbotFrame
        self.text.bind('<Return>', self.chatbot_frame.pass_process())

        llm_response = self.llm_app.invoke(
            question=user_input, 
            chat_history=self.chatbot_frame.chat_history, # Atribute from ChatbotFrame
            is_error_message=True
        )
        response_items = llm_response.get_response_items()
        self.chatbot_frame.add_message(f"Bot: {response_items['generation']}") # Method from ChatbotFrame
        self.chatbot_frame.loading_frame.grid_forget() # Method from ChatbotFrame

        self.chatbot_frame.return_button_entry_after_threading() # Method from ChatbotFrame
        self.text.bind('<Return>', self.execute_command)

    def execute_command(self, event=None):
        command = self.get_input_command()
        if command.strip():
            self.text.insert(tk.END, "\n")
            self.text.see(tk.END)

        self.get_output_command(command)

        self.text.insert(tk.END, "\n")
        self.insert_prompt()
        return "break"

    def get_input_command(self):
        command = self.text.get("end-1c linestart", "end-1c")
        return command.split("$ ", 1)[-1].strip()
    
    def get_output_command(self, command):
        try:
            terminal_run = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            
            self.text.insert(tk.END, terminal_run.stdout)
        except subprocess.CalledProcessError as err:
            error_message = err.stderr
            self.text.insert(tk.END, error_message)

            self.chatbot_frame.loading_frame.grid(column=0, row=0) # Atribute from ChatbotFrame
            self.chatbot_frame.loading_screen() # Method from ChatbotFrame

            traceback_patter = r'File "(?P<filename>.*?)".*?\n\s*(?P<code>.*?)\n'
            matches = re.finditer(traceback_patter, error_message)
            list_matches = list(matches)
            with open(list_matches[0].group("filename"), "r") as f:
                script_code = f.read()
                print(script_code)

            user_input = f"Cara mengatasi error: \n{error_message} \nberdasarkan kode berikut: \n{script_code}"
            self.chatbot_frame.add_message(f"You: {error_message}") # Method from ChatbotFrame
            Thread(target=self.threading_llm, args=(user_input, )).start()