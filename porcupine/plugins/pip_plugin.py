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
        self.search_term.set('Please enter a PyPI package to search for...')
        # buttons and scroll bars initialized
        self.search_btn = ttk.Button(self.big_frame, text='Search', command=self.pip_search)
        self.search_btn.grid(row=0, column=4)
        self.search_btn.bind('<Return>', self.pip_search)
        self.install_btn = ttk.Button(self.big_frame, text='Install', command=self.pip_install)
        self.install_btn.grid(row=2, column=2)
        self.uninstall_btn = ttk.Button(self.big_frame, text='Uninstall', command=self.pip_uninstall)
        self.uninstall_btn.grid(row=2, column=1)
        self.list_or_search = 'search'
        self.pip_list_btn = ttk.Button(self.big_frame, text='Pip List', command=self.pip_list)
        self.pip_list_btn.grid(row=2, column=0)
        self.scrollbar = ttk.Scrollbar(self.big_frame, orient='vertical')
        self.search_results = []
        # listbox for search results
        self.listbox = tk.Listbox(self.big_frame, selectmode='browse', yscrollcommand=self.scrollbar.set)
        # global / user checkbox
        self.check_button_state = tk.IntVar()
        self.check_button = ttk.Checkbutton(self.big_frame, text='Global Install', variable=self.check_button_state)
        self.check_button_state.set(1)
        self.check_button.grid(row=2, column=4)

    def pip_search(self, list_or_search=0, e=None):
        self.search_results = []
        if list_or_search is 0:
            list_or_search = 'search'
        else:
            list_or_search = 'list'
        package = self.search_term.get()
        try:
            search = subprocess.check_output([sys.executable, '-m', 'pip', list_or_search, package])
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
        self.listbox.delete(0, tk.END)
        self.listbox.config(width=60)
        self.scrollbar.grid_anchor('e')
        for item in self.search_results:
            self.listbox.insert(tk.END, item)
        self.listbox.grid(row=1, columnspan=4)
        self.listbox.bind("<Double-Button-1>", self.pip_install)

    def pip_install(self, e=None):
        if e is None:
            package = self.search_term.get()
        else:
            package = self.listbox.get('active')
            package = package.split(' ')
            package = package[0]
        if not self.check_button_state.get():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', '{0}'.format(package)], input=b'y')
        else:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '{0}'.format(package)], input=b'y')

    def pip_uninstall(self):
        package = self.search_term.get()
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '{0}'.format(package)], input=b'y')

    def pip_list(self):
        self.pip_search(list_or_search=1)

    def run_gui(self):
        self.root.mainloop()


def setup():
    pip = PipGui()
    actions.add_command('Pip/Pip Search', pip.run_gui)


if __name__ == '__main__':
    pip = PipGui()
    pip.run_gui()
