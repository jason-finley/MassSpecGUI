import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from customlasso import myLassoSelector
from matplotlib import path
import numpy as np
import json
import os

# Fuction to calculate the average of selected region in a matrix
def getaverage(matrix, indices):
    lin = np.arange(matrix.size)
    flat_matrix = matrix.flatten()

    average = "None"
    if len(lin[indices]) != 0:
        average = np.average(flat_matrix[lin[indices]])

    return average

# Callback function for the lasso tool, calculating averages within the selected region
def onselect(verts, tensor):
    shape = tensor.shape
    pix_x = np.arange(shape[2])
    pix_y = np.arange(shape[1])
    xv, yv = np.meshgrid(pix_x, pix_y)
    pix = np.vstack((xv.flatten(), yv.flatten())).T

    p = path.Path(verts)
    indices = p.contains_points(pix, radius=1)

    averages = []
    for i in range(len(tensor)):
        averages.append(getaverage(tensor[i], indices))

    if averages[0] == "None":
        total_average = "None"
    else:
        total_average = sum(averages) / len(averages)

    return total_average, averages

# Function to save data to a JSON file
def save_data(fname, lassos, radio_sel):
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
            "Total Average": lassos[i].total_average,
            "Averages": lassos[i].averages,
            "Type": radio_sel[i].get(),
            "Points": points
        }

    json.dump(data, file)

# Function to display data from a JSON file
def display_data(fname, lassos, radio_sel, labels):
    file = open(fname + ".json", "r")
    data = json.load(file)

    for i in range(len(lassos)):
        lassos[i].total_average = data[str("BOX" + str(i))]["Total Average"]
        labels[i].config(text = lassos[i].total_average)

        lassos[i].averages = data[str("BOX" + str(i))]["Averages"]

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

# Function to display the main window
def display_main(master, npy_files, num_slice):
    print("DISPLAYING SLICE NUMBER:", num_slice)
    root = tk.Toplevel(master)
    root.title("Submatrix Average Calculator")
    root.geometry('900x750')
    root.configure(bg='white')
    
    figure1 = plt.Figure(figsize=(9, 3), dpi=100)
    figure2 = plt.Figure(figsize=(9, 3), dpi=100)

    m = 0 # add matplot figures to subplots and add subplots to plots list
    plots = []
    for i in range(len(npy_files)):
        m += 1
        if m <= 3:
            subplot = figure1.add_subplot(130 + m)
        else:
            subplot = figure2.add_subplot(130 + m - 3)

        subplot.matshow(npy_files[i][num_slice], cmap='gray', origin='lower')
        subplot.set_aspect(30)
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
    for i in range(len(npy_files)):
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
        lassos.append(myLassoSelector(plots[i], onselect, tensor = npy_files[i], label = labels[i]))


    # file name entry box
    fname_var=tk.StringVar()
    fname_entry = tk.Entry(root, textvariable = fname_var, font=('calibre',18,'normal'), bg="gray")
    fname_entry.place(x=328, y=620)

   
    # create Save button and Display button
    btn1 = tk.Button(root, text = 'Save', command = lambda: save_data(fname_var.get(), lassos, radio_sel))
    btn1.grid(row=2, column=0, pady=60, ipadx=80, ipady=15)

    btn2 = tk.Button(root, text = 'Display', command = lambda: display_data(fname_var.get(), lassos, radio_sel, labels))
    btn2.grid(row=2, column=1, pady=60, ipadx=80, ipady=15)


def adjust_tensor(entry):
    if entry == "":
        entry = 0

    return int(entry)

# Main function to initialize and run the program
def main():
    directory = "/scratch/gilbreth/jpfinley/numpy_read/read_raw_data/Laskin_data/"

    try:
        os.path.isfile(directory)
        folder_names = os.listdir(directory)
    except:
        print("Folder: {directory} does not exist.")

    npy_files = []

    for folder_name in folder_names:
        file_names = os.listdir(directory + folder_name)
        print(f"Accessing folder: {folder_name}.")

        npy_files_of_folder = []

        for file_name in file_names:
            print(file_name)
            if file_name != 'pixelsCeramides.npy' and file_name != 'pixelsPE_LPE_norm.npy':
                npy_file = np.load(directory + folder_name + "/" + file_name)
                npy_files_of_folder.append(npy_file)
                shape = npy_file.shape
                print("File", file_name, "contains", shape[0], "slices with pixel dimensions:", shape[2], "by", shape[1])

        npy_files.append(np.concatenate(npy_files_of_folder))

    for npyfile in npy_files:
        print(npyfile.shape)


    # create main window
    master = tk.Tk()
    master.title("Submatrix Average Calculator")
    master.geometry('570x350')
    master.configure(bg='white')
    
    entry = tk.Entry(master, font=('calibre', 18, 'normal'), bg="gray")
    entry.grid(row=1, column=1, padx=10, pady=20, ipady=5)

    # create tensor display window with adjusted tensor
    btnmain = tk.Button(master, text = 'Load', command = lambda: display_main(master, npy_files, adjust_tensor(entry.get())))
    btnmain.grid(row=3, column=1, pady=20, ipadx=80, ipady=15)

    master.mainloop()

# Run the main function to start the program
main()
