import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from customlasso import myLassoSelector
from matplotlib import path
import numpy as np
import json
import os


def getaverage(matrix, indices): # determine average
    lin = np.arange(matrix.size)
    flat_matrix = matrix.flatten()
    
    average = None
    if len(lin[indices]) != 0:
        average = np.average(flat_matrix[lin[indices]])
    else:
        average = "None"
    
    return average


def onselect(verts, matrix): # using the lasso tool
    pix = np.arange(100)
    xv, yv = np.meshgrid(pix,pix)
    pix = np.vstack( (xv.flatten(), yv.flatten()) ).T

    p = path.Path(verts)
    indices = p.contains_points(pix, radius=1)

    return getaverage(matrix, indices)


def save_data(fname, lassos, radio_sel): # save data to json file
    file = open(fname + ".json", "w")
    data = {}

    for i in range(len(lassos)):
        x_values = []
        y_values = []
        if lassos[i].verts is not None:
            for point in lassos[i].verts:
                x_values.append(point[0])
                y_values.append(point[1])

        points = (x_values, y_values)

        data[str("BOX" + str(i))] = {
            "Average": lassos[i].average,
            "Type": radio_sel[i].get(),
            "Points": points
        }

    json.dump(data, file)


def display_data(fname, lassos, radio_sel, labels):
    file = open(fname + ".json", "r")
    data = json.load(file)

    for i in range(len(lassos)):
        lassos[i].average = data[str("BOX" + str(i))]["Average"]
        labels[i].config(text = lassos[i].average)

        lassos[i].type = data[str("BOX" + str(i))]["Type"]
        radio_sel[i].set(lassos[i].type)

        points = data[str("BOX" + str(i))]["Points"]
        verts = []
        for j in range(len(points[0])):
            verts.append([points[0][j], points[1][j]])
        lassos[i].verts = verts
        
        lassos[i]._selection_artist.set_visible(True)
        lassos[i]._selection_artist.set_data(points)
        lassos[i].update()
        lassos[i]._selection_artist.set_visible(False)


def display_main(master, tensor):
    root = tk.Toplevel(master) # create window
    root.title("Submatrix Average Calculator")
    root.geometry('900x750')
    root.configure(bg='white')

    figure1 = plt.Figure(figsize=(9, 3), dpi=100) # size of plots
    figure2 = plt.Figure(figsize=(9, 3), dpi=100)

    i = 0 # add matplot figures to subplots and add subplots to plots list
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
    bar1.get_tk_widget().grid(row=0, columnspan=2)

    bar2 = FigureCanvasTkAgg(figure2, root) # second row of plots
    bar2.get_tk_widget().grid(row=1, columnspan=2)
    

    # create radio buttons and average labels for each plot
    radio_sel = []
    labels = []
    y_coord = -40
    for i in range(len(tensor)):
        selected = tk.StringVar() # initial radio button value
        selected.set("null")
        
        if i%3 == 0: # increase y coordinate for next row
            y_coord += 300

        r1 = tk.Radiobutton(root, text='Group A', variable=selected, value='A') # radio buttons
        r1.place(x=130 + (i%3)*250, y=y_coord)
        r2 = tk.Radiobutton(root, text='Group B', variable=selected, value='B')
        r2.place(x=220 + (i%3)*250, y=y_coord)
        label = tk.Label(root, text = "None")
        label.place(x=175 + (i%3)*250, y=y_coord+30)

        radio_sel.append(selected) # add button selection and labels to list
        labels.append(label)

    # create lasso tools for each plot
    lassos = []
    for i in range(len(plots)):
        lassos.append(myLassoSelector(plots[i], onselect, matrix = tensor[i], label = labels[i]))


    # file name entry box
    fname_var=tk.StringVar()
    fname_entry = tk.Entry(root, textvariable = fname_var, font=('calibre',18,'normal'), bg="gray")
    fname_entry.place(x=328, y=620)

   
    # create Save button and Display button
    btn1 = tk.Button(root, text = 'Save', command = lambda: save_data(fname_var.get(), lassos, radio_sel))
    btn1.grid(row=2, column=0, pady=60, ipadx=80, ipady=15)

    btn2 = tk.Button(root, text = 'Display', command = lambda: display_data(fname_var.get(), lassos, radio_sel, labels))
    btn2.grid(row=2, column=1, pady=60, ipadx=80, ipady=15)


def adjust_tensor(directory, entries):
    loaded_tensor = np.load(directory)
    shape = loaded_tensor.shape

    coords = []
    for entry in entries:
        try:
            coords.append(int(entry.get()))
        except:
            coords.append(0)
    
    for i in range(len(coords)):
        if coords[i] < 0:
            coords[i] = 0
        if coords[i] > shape[int(i/2)]:
            coords[i] = shape[int(i/2)]
    
    print("coords: ", coords)

    displayed_tensor = loaded_tensor[coords[0]:coords[1], coords[2]:coords[3], coords[4]:coords[5]]
    shape = displayed_tensor.shape
    
    pads = [0, 0, 0]
    if shape[0] < 6:
        pads[0] = 6 - shape[0]
    if shape[1] < 100:
        pads[1] = 100 - shape[1]
    if shape[2] < 100:
        pads[2] = 100 - shape[2]

    pads = [6 - shape[0], 100 - shape[1], 100 - shape[2]]
    displayed_tensor = np.pad(displayed_tensor, pad_width=((0, pads[0]), (0, pads[1]), (0, pads[2])))

    return displayed_tensor


def main():
    directory = "/scratch/gilbreth/jpfinley/numpy_read/read_raw_data/Laskin data/1_1013 WT F2/pixelsFA_d8AA_norm.npy"

    # create main window
    master = tk.Tk()
    master.title("Submatrix Average Calculator")
    master.geometry('570x350')
    master.configure(bg='white')

    entries = []
    
    for i in range(6):
        entries.append(tk.Entry(master, font=('calibre', 18, 'normal'), bg="gray"))
        entries[i].grid(row=int(i/2), column=i%2, padx=10, pady=20, ipady=5)

    # create tensor display window with adjusted tensor
    btnmain = tk.Button(master, text = 'Load', command = lambda: display_main(master, adjust_tensor(directory, entries)))
    btnmain.grid(row=3, column=0, pady=20, ipadx=80, ipady=15)

    master.mainloop()


main()
