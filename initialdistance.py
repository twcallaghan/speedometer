import tkinter as tk
import cv2

global x1, y1, x2, y2


def setmouse(event):
    global x1, y1, x2, y2
    if x1 is None:
        x1 = event.x
        y1 = event.y
    else:
        x2 = event.x
        y2 = event.y


class InitialDistance:
    def __init__(self):
        self.startpointx = 0
        self.endpointx = 0
        self.diffx = None
        self.canvas = None
        self.canvas2 = None
        self.inchesentry = None
        self.inchperpixel = 1
        self.root = None
        self.mousex = None
        self.mousey = None

    def mouseclick(self):
        global x1, y1, x2, y2
        if self.startpointx == 0:
            self.startpointx = x1
        else:
            self.endpointx = x2
            self.diffx = abs(self.startpointx - self.endpointx)
        if x1 is not None:
            self.canvas.create_rectangle((x1 - 50), (y1 - 50), 100, 100, outline="#fb0", fill="#fb0")
            if x2 is not None:
                self.canvas.create_rectangle((x2 - 50), (y2 - 50), 100, 100, outline="#fb0", fill="#fb0")
                self.canvas.create_line(x1, y1, x2, y2)

    def finish(self):
        if self.diffx is not None and self.inchesentry is not None:
            self.inchperpixel = self.inchesentry.get() / self.diffx
            self.root.destroy()

    def getinitialdistance(self):
        global x1, y1, x2, y2
        x1, y1, x2, y2 = None, None, None, None
        # Make it so the user can input a given distance to then calculate speed for cars moving
        cv2.destroyAllWindows()

        self.root = tk.Tk()
        self.root.title("Give initial distance")
        w = 1920
        h = 1080

        # Make a canvas
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg='white')
        if x2 is None:
            self.canvas.bind("<Button-1>", setmouse)

        donebutton = tk.Button(self.canvas, text="Done", fg="red", command=InitialDistance.mouseclick(self))
        donebutton.pack(side=tk.LEFT)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        image = tk.PhotoImage(file="./firstframe.ppm")
        self.canvas.create_image(0, 0, image=image, anchor=tk.NW)

        self.canvas2 = tk.Canvas(self.root, width=w, height=h, bg='white')
        self.inchesentry = tk.Entry(self.root)
        self.canvas2.create_window(20, 20, window=self.inchesentry)
        button1 = tk.Button(text='Enter how many inches the measurement is', command=InitialDistance.finish(self))
        self.canvas2.create_window(20, 80, window=button1)
        self.canvas2.pack()

        self.root.mainloop()
