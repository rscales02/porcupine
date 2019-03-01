# encoding='utf-8'
from porcupine import actions

import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import sys
import threading
import os
import queue


class PipGui:
    """
    A graphic user interface for interacting with the pip command
    """
    def __init__(self):
        # create root window
        self.root = tk.Toplevel()
        self.root.title('Pip GUI')
        self.root.geometry("500x300+250+100")
        # replace with ttk for aesthetics
        self.big_frame = ttk.Frame(self.root)
        self.big_frame.pack(fill='both', expand=True)
        # entry field with string variable of package to be found
        self.search_term = tk.StringVar()
        self.entry = ttk.Entry(self.big_frame, textvariable=self.search_term)
        self.entry.config(width=55)
        self.entry.grid(row=0, column=0, columnspan=3)
        self.search_term.set('Please enter a PyPI package to search for...')
        # buttons and scroll bars initialized
        self.search_btn = ttk.Button(self.big_frame, text='Search', command=self.pip_search)
        self.search_btn.grid(row=0, column=4)
        self.search_btn.bind('<Return>', self.pip_search)
        self.install_btn = ttk.Button(self.big_frame, text='Install', command=self.pip_install)
        self.install_btn.grid(row=2, column=2)
        self.uninstall_btn = ttk.Button(self.big_frame, text='Uninstall', command=self.pip_uninstall)
        self.uninstall_btn.grid(row=2, column=1)
        self.pip_list_btn = ttk.Button(self.big_frame, text='List', command=self.pip_list)
        self.pip_list_btn.grid(row=2, column=0)
        self.scrollbar = ttk.Scrollbar(self.big_frame, orient='vertical')
        # listbox for search results
        self.listbox = tk.Listbox(self.big_frame, selectmode='browse')
        self.listbox.config(width=60)
        self.listbox.grid(row=1, column=0, columnspan=5)
        # global / user checkbox
        self.check_button_state = tk.IntVar()
        self.check_button = ttk.Checkbutton(self.big_frame, text='Global Install', variable=self.check_button_state)
        self.check_button_state.set(1)
        self.check_button.grid(row=2, column=4)
        # thread for async response out of main loop
        self.thread = threading.Thread(target=self.pip_thread)
        # queue for communication between mainloop and thread
        self.the_queue = queue.Queue()
        # dictionary for pip options
        self.pip_dict = {
            'process': '',
            'global': '',
            'package': ''
        }

    def pip_search(self, e=None):
        self.pip_dict['process'] = 'search'
        self.start_pip_thread()

    def pip_list(self):
        self.pip_dict['process'] = 'list'
        self.start_pip_thread()

    def pip_install(self, e=None):
        self.pip_dict['process'] = 'install'
        self.start_pip_thread()

    def pip_uninstall(self):
        self.pip_dict['process'] = 'uninstall'
        self.start_pip_thread()

    def start_pip_thread(self):
        self.pip_dict['package'] = self.search_term.get()
        if not self.check_button_state.get():
            self.pip_dict['global'] = '--user'
        else:
            self.pip_dict['global'] = ''
        self.the_queue.put(self.pip_dict)
        self.thread.start()
        self.root.after(200, self.is_thread_live)

    def pip_thread(self):
        try:
            pip_dict = self.the_queue.get(block=False)
        except queue.Empty:
            print('empty queue')

        try:
            sp = subprocess.Popen([sys.executable, '-m', 'pip', pip_dict['process'], pip_dict['global'],
                                   pip_dict['package']], stdout=subprocess.PIPE)
            response = sp.communicate()
        except subprocess.SubprocessError as err:
            print(err)
        self.the_queue.put(response)

    def is_thread_live(self):
        if self.thread.is_alive():
            print('its alive!!')
            self.root.after(2000, self.is_thread_live())
        elif self.pip_dict['process'] is 'search' or 'list':
            self.display_search_results()
        else:
            print('dead')

    def display_search_results(self):
        self.is_thread_live()
        try:
            search_results = self.the_queue.get(block=False)
            self.root.tk.splitlist(search_results)
        except subprocess.SubprocessError as er:
            print('display_search_results error', er)
        self.listbox.delete(0, tk.END)
        for item in search_results:
            self.listbox.insert(tk.END, item)
        self.listbox.bind("<Double-Button-1>", self.pip_install)

    def run_gui(self):
        self.root.wait_window()


def create_gui():
    return PipGui()


def setup():
    actions.add_command('Pip/Pip Search', create_gui)


if __name__ == '__main__':
    main = tk.Tk()
    main.withdraw()

    pip = PipGui()
    pip.run_gui()
