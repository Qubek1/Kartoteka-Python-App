import ttkbootstrap as ttk

window = ttk.Window(themename="flatly")

noteBook = ttk.Notebook(master=window)
noteBook.pack(pady=20)

frame0 = ttk.Frame(master=noteBook)
frame1 = ttk.Frame(master=noteBook)
frame2 = ttk.Frame(master=noteBook)

frame0.pack(pady=100, padx=100)
frame1.pack(pady=100, padx=100)
frame2.pack(pady=100, padx=100)

noteBook.add(frame0, text = 'Tab1')
noteBook.add(frame1, text = 'Tab2')
noteBook.add(frame2, text = 'Tab3')
current_max_tab = 3

def add_tab():
    new_frame = ttk.Frame(master=noteBook)
    new_frame.pack(pady=100, padx=100)
    noteBook.add(new_frame, text="Tab"+str(current_max_tab))

button = ttk.Button(master=window, text="Add Tab", command=add_tab)
button.pack()

window.mainloop()