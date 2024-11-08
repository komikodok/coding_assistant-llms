import tkinter as tk
from tkinter import Scrollbar, Canvas, PhotoImage
from PIL import Image, ImageTk, ImageSequence

from threading import Thread
from langchain_core.messages import AIMessage, HumanMessage
from llms.llm_app import LLMApp


class ChatbotFrame:
    def __init__(self, root):
        self.llm_app = LLMApp()
        self.chat_history = [
            HumanMessage(content="Halo"),
            AIMessage(content="Halo juga!")
        ]

        self.root = root

        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = Canvas(self.frame)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.scroll_y = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.grid(row=0, column=1, sticky='ns')

        self.scroll_x = Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.grid(row=1, column=0, sticky='ew')

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.input_frame = tk.Frame(self.frame)
        self.input_frame.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.clear_button = tk.Button(self.input_frame, text="Clear All")
        self.clear_button.pack(side="left", padx=10)
        self.clear_button.bind("<Button-1>", self.clear_chat)

        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.input_entry.bind('<Return>', self.process_input)

        self.send_button = tk.Button(self.input_frame, text="Send")
        self.send_button.pack(side="right", padx=10)
        self.send_button.bind("<Button-1>", self.process_input)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_rowconfigure(2, weight=0)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)
        
        self.loading_frame = tk.Frame(self.frame)

        self.gif_path = "gui\loading_image\loading1.gif"
        self.gif = Image.open(self.gif_path)
        self.frames_gif = [ImageTk.PhotoImage(frame.resize((80, 80), Image.Resampling.LANCZOS)) for frame in ImageSequence.Iterator(self.gif)]

        self.frames_index = 0
        self.loading_gif_label = tk.Label(self.loading_frame, image=self.frames_gif[self.frames_index])
        self.loading_gif_label.grid()

        self.loading_text_label = tk.Label(self.loading_frame, text="Loading....")
        self.loading_text_label.grid()

    def process_input(self, event=None):
        def threading_llm(user_input):
            self.freeze_button_entry_while_threading()
            llm_response = self.llm_app.invoke(
                    question=user_input, 
                    chat_history=self.chat_history, 
                    is_error_message=False
            )
            # Response items = {"question": .., "generation": .., "chat_history": [..], "is_error_message": bool}
            response_items = llm_response.get_response_items()

            self.add_message(f"Bot: {response_items['generation']}")
            self.loading_frame.grid_forget()

            self.return_button_entry_after_threading()
            
        user_input = self.input_entry.get()
        if user_input.strip():
            self.add_message(f"You: {user_input}")
            self.input_entry.delete(0, tk.END)
    
            self.loading_frame.grid(column=0, row=0)
            self.loading_screen()
            Thread(target=threading_llm, args=(user_input, )).start()

    def add_message(self, message):
        message_label = tk.Label(self.scrollable_frame, text=message, anchor="w", justify="left")
        message_label.pack(fill='x', padx=10, pady=5)

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)  

    def clear_chat(self, event=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.chat_history = []
        self.canvas.update_idletasks()

    def loading_screen(self):
        self.frames_index = (self.frames_index + 1) % len(self.frames_gif)
        self.loading_gif_label.configure(image=self.frames_gif[self.frames_index])
        self.loading_frame.after(100, self.loading_screen)
        if self.frames_index == len(self.frames_gif):
            self.frames_index = 0

    def freeze_button_entry_while_threading(self):
        self.clear_button.bind("<Button-1>", self.pass_process)
        self.input_entry.bind("<Return>", self.pass_process)
        self.send_button.bind("<Button-1>", self.pass_process)

    def return_button_entry_after_threading(self):
        self.clear_button.bind("<Button-1>", self.clear_chat)
        self.input_entry.bind("<Return>", self.process_input)
        self.send_button.bind("<Button-1>", self.process_input)

    def pass_process(self, event=None):
        pass