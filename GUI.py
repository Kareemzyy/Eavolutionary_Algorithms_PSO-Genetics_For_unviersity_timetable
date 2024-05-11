from tkinter import *
from tkinter import ttk
import pandas as pd


def displaying_table(df, fitness_val):
    main_root = Tk()
    main_root.title('EA Project')

    # ------ Centring the window. ------ #
    width = 1000
    height = 500
    screen_width = main_root.winfo_screenwidth()
    screen_height = main_root.winfo_screenheight()
    x_root = (screen_width - width) // 2
    y_root = (screen_height - height) // 2
    main_root.geometry(f'{width}x{height}+{x_root}+{y_root}')

    # ------ Putting the label of the fitness. ------ #
    label_style = {
        'font': ('Comic Sans MS', 14),
    }
    ft_lb = Label(main_root, text=f'The fitness is : {fitness_val}', **label_style)
    ft_lb.pack()

    # ------ Putting the table. ------ #
    table = ttk.Treeview(main_root, columns=('1', '2', '3', '4'), show='headings')
    table.heading('1', text='Day')
    table.heading('2', text='Time Slot')
    table.heading('3', text='Hall')
    table.heading('4', text='Course & Professor')
    table.pack(fill=BOTH, expand=True)

    # Inserting values in the table. #
    # df = pd.read_csv('Schedule.csv')
    for idx in range(45):
        table.insert(parent='', index=idx, values=(df.iloc[idx, 0], df.iloc[idx, 1], df.iloc[idx, 2], df.iloc[idx, 3]))

    main_root.mainloop()

