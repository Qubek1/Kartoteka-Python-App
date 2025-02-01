import tkinter as tk
import ttkbootstrap as ttk

def convert():
    output_string.set(round(entry_double.get() / 0.621371192, 2))

window = ttk.Window(themename = 'flatly')
window.title('Demo')
window.geometry("300x150")

title_label = ttk.Label(master = window, text = 'Miles to kilometers', font = 'Calibri 24 bold')
title_label.pack()

input_frame = ttk.Frame(master = window)
entry_double = tk.DoubleVar()
entry = ttk.Entry(master = input_frame, textvariable = entry_double)
button = ttk.Button(master = input_frame, text = 'Convert', command = convert)
entry.pack(side = 'left', padx = 10)
button.pack(side = 'left')
input_frame.pack(pady = 10)

output_string = tk.StringVar()
output_label = ttk.Label(master = window, text = 'Output', font = 'Calibri 24', textvariable=output_string)
output_label.pack()


window.mainloop()
