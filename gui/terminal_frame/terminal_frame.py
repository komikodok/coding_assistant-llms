import tkinter as tk
from tkinter import Scrollbar
import subprocess
import os

from threading import Thread
import re
from coding_assistant.llms.llm_app import LLMApp


class TerminalFrame:
    def __init__(self, root, chatbot_frame):
        self.chatbot_frame = chatbot_frame
        self.llm_app = LLMApp()

        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Scrollbar vertikal untuk terminal
        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Widget Text untuk terminal output dan input
        self.text = tk.Text(self.frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set, bg="black", fg="white")
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.bind('<Return>', self.execute_command)

        # Menghubungkan scrollbar dengan Text widget
        self.scrollbar.config(command=self.text.yview)

        # Inisialisasi dengan working directory di terminal
        self.insert_prompt()

    def insert_prompt(self):
        # Menampilkan awalan dengan current working directory di terminal
        cwd = os.getcwd()
        self.text.insert(tk.END, f"{cwd}$ ")
        self.text.mark_set("insert", "end-1c")
        self.text.see(tk.END)

    def threading_llm(self, user_input):
        # Freeze tombol dan entry ketika proses threading llm_invoke
        self.chatbot_frame.freeze_button_entry_while_threading() # Method dari class ChatbotFrame
        self.text.bind('<Return>', self.chatbot_frame.pass_process())

        llm_response = self.llm_app.invoke(
            question=user_input, 
            chat_history=self.chatbot_frame.chat_history, # Atribute dari class ChatbotFrame
            is_error_message=True
        )
        response_items = llm_response.get_response_items()
        # Menampilkan response bot ke dalam chatbot
        self.chatbot_frame.add_message(f"Bot: {response_items['generation']}") # Method dari class ChatbotFrame
        self.chatbot_frame.loading_frame.grid_forget() # Method dari class ChatbotFrame

        # Mengembalikan tombol dan entry ke dalam keadaan semula setelah proses threading_llm
        self.chatbot_frame.return_button_entry_after_threading() # Method dari class ChatbotFrame
        self.text.bind('<Return>', self.execute_command)

    def execute_command(self, event=None):

        # Mendapatkan perintah yang dimasukkan oleh pengguna di terminal
        command = self.get_input_command()
        if command.strip():
            # Pindah ke baris baru sebelum menampilkan output
            self.text.insert(tk.END, "\n")
            self.text.see(tk.END)

        self.get_output_command(command)

        # Pindah ke baris baru dan menampilkan prompt kembali
        self.text.insert(tk.END, "\n")
        self.insert_prompt()
        return "break"

    def get_input_command(self):
        # Mendapatkan teks yang diinput dari prompt terakhir hingga akhir teks
        command = self.text.get("end-1c linestart", "end-1c")
        return command.split("$ ", 1)[-1].strip()
    
    def get_output_command(self, command):
        try:
            # Menjalankan perintah
            terminal_run = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            
            # Menampilkan output di terminal jika tidak terjadi error
            self.text.insert(tk.END, terminal_run.stdout)
        except subprocess.CalledProcessError as err:
            error_message = err.stderr
            # Menampilkan output error di terminal jika terjadi error
            self.text.insert(tk.END, error_message)

            self.chatbot_frame.loading_frame.grid(column=0, row=0) # Atribute dari class ChatbotFrame
            self.chatbot_frame.loading_screen() # Method dari class ChatbotFrame

            # Menggunakan regex untuk menangkap kode program berdasarkan path dari traceback
            traceback_patter = r'File "(?P<filename>.*?)".*?\n\s*(?P<code>.*?)\n'
            matches = re.finditer(traceback_patter, error_message)
            list_matches = list(matches)
            with open(list_matches[0].group("filename"), "r") as f:
                script_code = f.read()
                print(script_code)

            user_input = f"Cara mengatasi error: \n{error_message} \nberdasarkan kode berikut: \n{script_code}"
            # Menampilkan error dari terminal ke dalam chatbot
            self.chatbot_frame.add_message(f"You: {error_message}") # Method dari class ChatbotFrame
            Thread(target=self.threading_llm, args=(user_input, )).start()