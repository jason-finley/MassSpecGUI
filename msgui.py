from graphics import *
from time import sleep
import numpy as np
from PIL import Image, ImageTk
import json


def window():
    win = GraphWin("GUI", 890, 790) # gui window
    win.setBackground("white")

    grid = Rectangle(Point(0, 0), Point(900, 587)) # clickable area

    input_box = Entry(Point(300, 657.5), 28) # input box
    input_box.setStyle("bold")
    input_box.setSize(20)
    input_box.draw(win)

    Submit = Rectangle(Point(645, 620), Point(815, 695)) # Submit button
    Submit.setFill("green")
    Submit.draw(win)
    sub_label = Text(Point(730, 657.5), "Submit")
    sub_label.setStyle("bold")
    sub_label.setSize(24)
    sub_label.setFill("black")
    sub_label.draw(win)

    return win, grid, input_box, Submit

def clicked(click, rect): # boolean if click was inside rectangle
    if not click:
        return False
    mx, my = click.getX(), click.getY()
    x1, y1 = rect.getP1().getX(), rect.getP1().getY()
    x2, y2 = rect.getP2().getX(), rect.getP2().getY()

    return (x1 < mx < x2) and (y1 < my < y2)


def get_tensor(): # create radom tensor
    tensor = np.random.randint(0, 100, size=(6, 100, 100))
    return tensor


def draw_imgs(image_size, padding_size, win, tensor): # draw tensor images onto window
    imgs = []

    for matrix in tensor: # turn matrices to images in imgs list
        img = ImageTk.PhotoImage(image=Image.fromarray(matrix))
        loaded_matrix = Image.fromarray(matrix)
        resized_matrix = loaded_matrix.resize(image_size)
        img = ImageTk.PhotoImage(resized_matrix)
        imgs = imgs + [img]

    i = padding_size + image_size[0]/2
    j = padding_size + image_size[1]/2
    for img in imgs: # draw imgs from imgs list
        img = TImage(Point(i, j), img)
        img.draw(win)
        i += image_size[0] + padding_size
        if i > 900: # move to next row if needed
            j += padding_size + image_size[1]
            i = padding_size + image_size[0]/2


def adjustipoint(t): # adjust inital point onto image
    if t < 35:
        return 35
    elif 285 < t < 302.5:
        return 285
    elif 302.5 < t < 320:
        return 320
    elif 570 < t < 587.5:
        return 570
    elif 587.5 < t < 607:
        return 605
    elif t > 855:
        return 855
    else:
        return t
    

def whichimg(t): # determine selected image
    if 34 < t < 286:
        return 1
    elif 319 < t < 571:
        return 2
    elif 604 < t < 856:
        return 3
    
def secondclickloop(win, grid, box, column_num, row_num, matrix, image_size, xi, yi, sel):
    click = False # wait for second click loop
    while not clicked(click, grid):
        click = win.checkMouse()

        xf = win.winfo_pointerx() - win.winfo_rootx() # determine current cursor posistion
        yf = win.winfo_pointery() - win.winfo_rooty()

        xf = adjustfpoint(column_num, xf) # keep point inside image
        yf = adjustfpoint(row_num, yf)

        if sel == 0:
            rxi, rxf = xi - 35, xf - 35
            ryi, ryf = yi - 35, yf - 35
        elif sel == 1:
            rxi, rxf = xi - 320, xf - 320
            ryi, ryf = yi - 35, yf - 35
        elif sel == 2:
            rxi, rxf = xi - 605, xf - 605
            ryi, ryf = yi - 35, yf - 35
        elif sel == 3:
            rxi, rxf = xi - 35, xf - 35
            ryi, ryf = yi - 320, yf - 320
        elif sel == 4:
            rxi, rxf = xi - 320, xf - 320
            ryi, ryf = yi - 320, yf - 320
        elif sel == 5:
            rxi, rxf = xi - 605, xf - 605
            ryi, ryf = yi - 320, yf - 320

        sleep(0.03) # draw current rectangle
        box.undraw()
        box = Rectangle(Point(xi, yi), Point(xf, yf))
        box.setOutline("Light Blue")
        box.draw(win)
    
    box.setOutline("Blue") # indicate final click

    if xi > xf: # make initial point lower than final point
        xi, xf = xf, xi
    if yi > yf:
        yi, yf = yf, xi

    rpoints = [rxi, ryi, rxf, ryf] # relative points on image

    return getAverage(matrix, row_num, column_num, rxi, ryi, rxf, ryf, image_size), box, rpoints
    
        
def adjustfpoint(num, t): # adjust final point onto image
    if num == 1:
        if t < 35:
            return 35
        elif t > 285:
            return 285
        else:
            return t
    elif num == 2:
        if t < 320:
            return 320
        elif t > 570:
            return 570
        else:
            return t
    elif num == 3:
        if t < 605:
            return 605
        elif t > 855:
            return 855
        else:
            return t


def getAverage(matrix, row_num, column_num, rxi, ryi, rxf, ryf, image_size):
    y_scale, x_scale = image_size[1] / len(matrix), image_size[0] / len(matrix[0]) # determine scale of images
    y1, y2, x1, x2 = int(ryi / y_scale), int(ryf / y_scale), int(rxi / x_scale), int(rxf / x_scale) # return submatrix indexes

    average = np.average(matrix[y1:y2 + 1, x1:x2 + 1]) # average of submatrix

    return average

    

def main():
    # get attributes
    win, grid, input_box, Submit = window()
    tensor = get_tensor()

    # draw images
    image_size = (250, 250)
    padding_size = 35
    draw_imgs(image_size, padding_size, win, tensor)

    # initial values
    points = []
    boxes = []
    for i in range(len(tensor)):
        points = points + [[0, 0, 0, 0]]
        boxes = boxes + [Rectangle(Point(points[int(i)][0], points[int(i)][1]), Point(points[int(i)][2], points[int(i)][3]))]

    averages = [0, 0, 0, 0, 0, 0]
    
    # main loop
    while True:
        click = win.checkMouse()
        
        if clicked(click, grid): # check if click was in clickable area
            # make sure initial click is on an image
            xi, yi = click.getX(), click.getY()
            xi = adjustipoint(xi)
            yi = adjustipoint(yi)

            column_num = whichimg(xi)
            row_num = whichimg(yi)

            # determine selected box
            if row_num == 1:
                if column_num == 1:
                    sel = 0
                elif column_num == 2:
                    sel = 1
                elif column_num == 3:
                    sel = 2
            elif row_num == 2:
                if column_num == 1:
                    sel = 3
                elif column_num == 2:
                    sel = 4
                elif column_num == 3:
                    sel = 5

            matrix = tensor[sel]
            box = boxes[sel]
            selected_average, boxes[sel], box_points = secondclickloop(win, grid, box, column_num, row_num, matrix, image_size, xi, yi, sel)
            averages[sel] = selected_average
            points[sel] = box_points

        if clicked(click, Submit): # save to json file
            out_file = open(input_box.getText() + ".json", "w")
            data = {}
        
            for i in range(len(averages)):
                data[str("BOX" + str(i))] = {
                    "Average": averages[int(i)],
                    "Points (x1,y1,x2,y2)": points[int(i)] 
                }

            json.dump(data, out_file)

            print(input_box.getText())
            print(data)


main()