# encoding='utf-8'
from porcupine import actions, utils

import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import sys
import threading
import os
import queue
import tempfile


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
        self.thread_list = []
        self.sp = None
        # queue for communication between mainloop and thread
        self.the_queue = queue.Queue()
        # dictionary for pip options
        self.pip_dict = {
            'process': '',
            'global': '',
            'package': ''
        }
        # initialize byte string to receive stdout response
        self.stdout = b''

    def pip_search(self, e=None):
        """
        update pip_dict and start thread for 'search'
        :param e:
        :return:
        """
        self.pip_dict['process'] = 'search'
        self.start_pip_thread()

    def pip_list(self):
        """
        update pip_dict and start thread for 'list'
        :return:
        """
        self.pip_dict['process'] = 'list'
        self.start_pip_thread()

    def pip_install(self, e=None):
        """
        update pip_dict and start thread for 'install'
        :param e:
        :return:
        """
        self.pip_dict['process'] = 'install'
        self.start_pip_thread()

    def pip_uninstall(self):
        """
        update pip_dict and start thread for 'uninstall'
        :return:
        """
        self.pip_dict['process'] = 'uninstall'
        self.start_pip_thread()

    def get_package_name(self):
        """
        update pip_dict with package name or empty string if using 'pip list'
        :return:
        """
        if self.pip_dict['process'] == list:
            self.pip_dict['package'] = ''
        else:
            self.pip_dict['package'] = self.search_term.get()

    def get_global_checkbox(self):
        """
        update pip_dict with global/user option
        :return:
        """
        if not self.check_button_state.get():
            self.pip_dict['global'] = '--user'
        else:
            self.pip_dict['global'] = ''

    def start_pip_thread(self):
        """
        populates the pip_dict and places it into the Queue for access from the thread
        append newest thread to thread_list
        start thread at the last position in the thread_list
        begins the recursive function to test whether or not the current thread is still active
        :return:
        """
        self.get_package_name()
        self.get_global_checkbox()
        self.the_queue.put(self.pip_dict)
        self.thread_list.append(threading.Thread(target=self.pip_thread))
        try:
            self.thread_list[-1].start()
        except RuntimeError as e:
            print(e)
        self.is_thread_live()

    def pip_thread(self):
        """
        pull pip_dict from queue
        begin the PIP subprocess
        :return: None
        """
        response = None
        try:
            pip_dict = self.the_queue.get(block=False)
        except queue.Empty:
            print('empty queue')
        try:
            self.sp = subprocess.Popen([sys.executable, '-u', '-m', 'pip', pip_dict['process'], '--no-cache',
                                        pip_dict['package']], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            # if not pip_dict['global'] and pip_dict['process'] == 'install':
            #     print('user')
            # else:
            #     self.sp = subprocess.Popen([sys.executable, '-m', 'pip', pip_dict['process'], pip_dict['package']],
            #                                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        except subprocess.SubprocessError as err:
            print(err)
        if pip_dict['process'] == 'uninstall' or pip_dict['process'] == 'install':
            x=0
            while True:
                # x += 1
                # print(x)
                # if x > 100:
                #     break
                try:
                    stdout = self.sp.stdout.read(1)
                    self.stdout += stdout
                    print(self.stdout)
                    if b'Proceed (y/n)?' in self.stdout:
                        try:
                            print('attempting response')
                            self.sp.stdin.write(b'y\n')
                            self.sp.stdin.flush()
                            break
                        except:
                            print('stdin write failed')
                except:
                    print('you fucked up')
                    break
        else:
            if response:
                pass
            else:
                response = self.sp.communicate()
            print('responded')
            self.the_queue.put(response)
        return

    def is_thread_live(self):
        """
        tests the last object in thread_list to check its activity state
        :return:
        """
        if self.thread_list[-1].is_alive():
            return self.root.after(100, self.is_thread_live)
        else:
            self.display_search_results()
            print('dead')

    def display_search_results(self, search_results=[]):
        """
        pull subprocess response from the queue
        make response readable and ordered
        display response
        :return:
        """
        try:
            search_results = list(self.the_queue.get(block=False))
            search_results = search_results[0].decode('utf-8')
            search_results = search_results.splitlines()
        except Exception as er:
            print('display_search_results error', er)
            return
        self.listbox.delete(0, tk.END)
        print(search_results)
        for item in search_results:
            item.strip()
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
