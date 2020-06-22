import tkinter as tk
import cv2
import math


class InitialDistance:
    def __init__(self):
        self.startpointx = 0
        self.startpointy = 0
        self.endpointx = 0
        self.endpointy = 0
        self.diffx = None
        self.diffy = None
        self.diff = None
        self.canvas = None
        self.root = None
        self.canvas2 = None
        self.inchesentry = None
        self.inches_var = None
        self.inchesperpixel = None
        self.run = True

    def mouseclick(self, event):
        if self.diff is not None:
            if self.inches_var is None:
                self.secwindowmain()
            return

        if self.startpointx == 0 and event.x != 0:
            self.startpointx = event.x
            self.startpointy = event.y
        elif event.x != 0:
            self.endpointx = event.x
            self.endpointy = event.y
            self.diffx = abs(self.startpointx - self.endpointx)
            self.diffy = abs(self.startpointy - self.endpointy)
            self.diff = math.sqrt(math.pow(self.diffx, 2) + math.pow(self.diffy, 2))
        if self.startpointx != 0:
            self.canvas.create_rectangle((self.startpointx - 30), (self.startpointy - 30), (self.startpointx + 30),
                                         (self.startpointy + 30), outline="#fb0", fill="#fb0")
            if self.endpointx != 0:
                self.canvas.create_rectangle((self.endpointx - 30), (self.endpointy - 30), (self.endpointx + 30),
                                             (self.endpointy + 30), outline="#fb0", fill="#fb0")
                self.canvas.create_line(self.startpointx, self.startpointy, self.endpointx, self.endpointy)

    def finish(self):
        if self.inchesentry.get() != '':
            self.inchesperpixel = int(self.inchesentry.get()) / self.diff
            self.root.destroy()
            self.run = False

    def secwindowmain(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.root.geometry("600x400")
        self.root.configure(background='white')
        inches_label = tk.Label(self.root, text='Inches of measurement: ')
        self.inches_var = tk.StringVar()
        self.inchesentry = tk.Entry(self.root, textvariable=self.inches_var)
        button1 = tk.Button(self.root, text='Press after entering how many inches the measurement is',
                            command=self.finish)
        inches_label.grid(row=0, column=0)
        self.inchesentry.grid(row=0, column=1)
        button1.grid(row=1, column=0)

    def main(self):
        # Make it so the user can input a given distance to then calculate speed for cars moving
        cv2.destroyAllWindows()

        self.root = tk.Tk()
        self.root.title("Give initial distance")
        w = 1920
        h = 1080

        # Make a canvas
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg='white')
        self.canvas.pack(expand=True, fill=tk.BOTH)
        image = tk.PhotoImage(file="./firstframe.ppm")
        self.canvas.create_image(0, 0, image=image, anchor=tk.NW)
        self.canvas.bind("<Button-1>", self.mouseclick)
        self.root.mainloop()
