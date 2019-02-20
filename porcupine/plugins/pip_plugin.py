# encoding='utf-8'
from porcupine import actions

import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import sys
import os


class PipGui:
    def __init__(self):
        # create root window
        self.root = tk.Tk()
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
        self.search_term.set('requests')
        # buttons and scroll bars initialized
        self.search_btn = ttk.Button(self.big_frame, text='Search', command=self.pip_search)
        self.search_btn.grid(row=0, column=4)
        self.search_btn.bind('<Return>', self.pip_search)
        self.install_btn = ttk.Button(self.big_frame, text='Install', command=self.pip_install)
        self.install_btn.grid(row=2, column=2)
        self.uninstall_btn = ttk.Button(self.big_frame, text='Uninstall', command=self.pip_uninstall)
        # self.uninstall_btn.grid(row=2, column=1)
        self.scrollbar = ttk.Scrollbar(self.big_frame, orient='vertical')
        self.search_results = []

    def pip_search(self, e=None):
        self.search_results = []
        package = self.search_term.get()
        try:
            search = subprocess.check_output([sys.executable, '-m', 'pip', 'search', package])
            # `search` returns a binary string
        except Exception as er:
            print('search unsuccessful', er)
        search = str(search, 'utf-8').split('\n')
        search = [item.strip() for item in search]
        search.sort()
        for item in search:
            if 'INSTALLED' in item:
                self.search_results.insert(0, item)
            elif item:
                self.search_results.append(item)
        if not search:
            self.search_results = (['No Search Results'])
        self.display_search_results()

    def display_search_results(self):
        assert isinstance(self.search_results, list)
        if 'INSTALLED' in self.search_results[0]:
            self.uninstall_btn.grid(row=2, column=1)
        listbox = tk.Listbox(self.big_frame, selectmode='browse', yscrollcommand=self.scrollbar.set)
        listbox.config(width=60)
        self.scrollbar.grid_anchor('e')
        for item in self.search_results:
            listbox.insert(tk.END, item)
        listbox.grid(row=1, columnspan=4)
        items = map(int, listbox.curselection())
        listbox.bind("<Double-Button-1>", self.pip_install)

    def pip_install(self, e=None):
        print(e)

    def pip_uninstall(self):
        package = self.search_term.get()
        subprocess.call([sys.executable, '-m', 'pip', 'uninstall', '{0}'.format(package)])

    def run_gui(self):
        self.root.mainloop()


def setup():
    pip = PipGui()
    actions.add_command('Pip/Pip Search', pip.run_gui)


if __name__ == '__main__':
    pip = PipGui()
    pip.run_gui()
