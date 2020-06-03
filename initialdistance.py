import tkinter as tk
import cv2


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

    def mouseclick(self, event):
        if self.startpointx == 0:
            self.startpointx = event.x
        else:
            self.endpointx = event.x
            self.diffx = abs(self.startpointx - self.endpointx)
        self.canvas.create_rectangle((event.x - 50), (event.y - 50), 100, 100, outline="#fb0", fill="#fb0")

    def finish(self):
        if self.diffx is not None and self.inchesentry is not None:
            self.inchperpixel = self.inchesentry.get() / self.diffx
            self.root.destroy()

    def getinitialdistance(self):
        # Make it so the user can input a given distance to then calculate speed for cars moving
        cv2.destroyAllWindows()

        self.root = tk.Tk()
        self.root.title("Give initial distance")
        w = 1920
        h = 1080

        # Make a canvas
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg='white')
        if self.diffx is None:
            self.canvas.bind("<Button-1>", InitialDistance.mouseclick())
        self.canvas.pack(expand=True, fill=tk.BOTH)
        image = tk.PhotoImage(file="./firstframe.ppm")
        self.canvas.create_image(0, 0, image=image, anchor=tk.NW)

        self.canvas2 = tk.Canvas(self.root, width=200, height=140, bg='white')
        self.inchesentry = tk.Entry(self.root)
        self.canvas2.create_window(20, 20, window=self.inchesentry)
        button1 = tk.Button(text='Enter how many inches the measurement is', command=InitialDistance.finish(self))
        self.canvas2.create_window(20, 80, window=button1)
        self.canvas2.pack()

        self.root.mainloop()
