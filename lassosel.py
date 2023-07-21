import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import LassoSelector
from matplotlib import path
import numpy as np
import json


def getaverage(matrix, indices): # determine average
    lin = np.arange(matrix.size)
    flat_matrix = matrix.flatten()
    average = np.average(flat_matrix[lin[indices]])
    
    return average


def onselect(verts, matrix): # using the lasso tool
    pix = np.arange(100)
    xv, yv = np.meshgrid(pix,pix)
    pix = np.vstack( (xv.flatten(), yv.flatten()) ).T

    p = path.Path(verts)
    indices = p.contains_points(pix, radius=1)

    return getaverage(matrix, indices)


def save_data(fname, lassos, radio_sel): # save data to json file
    out_file = open(fname + ".json", "w")
    data = {}

    for i in range(len(lassos)):
        data[str("BOX" + str(i))] = {
            "Average": lassos[i].average,
            "Type": radio_sel[i].get()
        }

    json.dump(data, out_file)


def main():
    root = tk.Tk() # create window
    root.title("Submatrix Average Calculator")
    root.geometry('900x750')
    root.configure(bg='white')

    tensor = np.random.randint(0, 100, size=(6, 100, 100)) # create matrices

    figure1 = plt.Figure(figsize=(9, 3), dpi=100) # size of plots
    figure2 = plt.Figure(figsize=(9, 3), dpi=100)


    i = 0
    plots = []
    for matrix in tensor:
        i += 1
        if i <= 3:
            subplot = figure1.add_subplot(130 + i)
        else:
            subplot = figure2.add_subplot(130 + i - 3)

        subplot.matshow(matrix, cmap='gray', origin='lower')
        subplot.axis('off')
        subplot.plot()
        plots.append(subplot)

    bar1 = FigureCanvasTkAgg(figure1, root) # first row of plots
    bar1.get_tk_widget().grid(row=0)

    bar2 = FigureCanvasTkAgg(figure2, root) # second row of plots
    bar2.get_tk_widget().grid(row=1)

    # create radio buttons for each plot
    radio_sel = []
    y_coord = -30
    for i in range(len(tensor)):
        selected = tk.StringVar() # initial radio button value
        selected.set("null")
        
        if i%3 == 0: # increase y coordinate for next row
            y_coord += 300

        r1 = tk.Radiobutton(root, text='Group A', variable=selected, value='A') # radio buttons
        r1.place(x=130 + (i%3)*250, y=y_coord)
        r2 = tk.Radiobutton(root, text='Group B', variable=selected, value='B')
        r2.place(x=220 + (i%3)*250, y=y_coord)

        radio_sel.append(selected) # add button selections to list

    # create lasso tools for each plot
    lassos = []
    for i in range(len(plots)):
        lassos.append(LassoSelector(plots[i], onselect, tensor[i]))

    # file name entry box
    fname_var=tk.StringVar()
    fname_entry = tk.Entry(root, textvariable = fname_var, font=('calibre',18,'normal'), bg="gray")
    fname_entry.place(x=328, y=610)

    # create save button
    btn = tk.Button(root, text = 'Save', command = lambda: save_data(fname_var.get(), lassos, radio_sel))
    btn.grid(row=2, pady=60, ipadx=80, ipady=15) 
    
    root.mainloop()

main()
