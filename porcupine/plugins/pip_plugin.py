# encoding='utf-8'
from porcupine import actions

import tkinter as tk
import tkinter.ttk as ttk
import pip
import time
import subprocess
import sys

# search = subprocess.check_output([sys.executable, '-m', 'pip', 'search', term])


class PipGui:
    def __init__(self):
        self.root = tk.Tk()
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)


def setup():
    actions.add_command('Pip/Pip Search')
    

if __name__ == '__main__':
    pass
