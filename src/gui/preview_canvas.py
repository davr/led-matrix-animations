from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
import math
import random

MAX_MODE = 1

class LED(object):
    def __init__(self, x, y, canvas):
        self.x = x
        self.y = y
        self.canvas = canvas

    def setColor(self, color):
        self.canvas.current_frame[self.y][self.x] = color

    def getColor(self):
        return self.canvas.current_frame[self.y][self.x]

class Matrix(object):
    def __init__(self, x, y, canvas):
        self.x = x
        self.y = y
        self.canvas = canvas

    def setColor(self, x, y, color):
        self.canvas.current_frame[self.y+y][self.x+x] = color
    
    def getColor(self, x, y):
        return self.canvas.current_frame[self.y+y][self.x+x]

class PreviewCanvas(QWidget):
    def __init__(self, width=480, height=480, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.current_frame = [ [0]*23 ]*23
        self.hue = 0
        self.tick = 0
        self.grid = 0
        self.outerRing = []
        self.middleRing = []
        self.innerRing = []
        self.matrix = Matrix(4, 9, self)
        self.generate_mask()  # Generate the mask when the widget is initialized
        self.mode = 0 

    def toggle_grid(self):
        self.grid += 1
        if(self.grid > 2):
            self.grid = 0
        self.update()

    def generate_mask(self):
        # Example frame data
        frame = [ [0]*23 ]*23        
        on = 0xFFFFFF

        # frame contains a 15x5 grid in the center, and then 3 rings of pixels around it
        # the inner most ring contains 12 positions, but only the top and bottom 3 are used (the other 6 overlap the central grid)
        # the next ring contains 24 positions, but only the top and bottom 9 are used (the other 6 overlap the central grid)
        # the outermost ring contains a full 24 positions
        # We will now fill these positions with 1s in frame:

        # Initialize the frame with zeros
        frame = [[0] * 23 for _ in range(23)]

        for y in range(0, 23):
            for x in range(0, 23):
                frame[y][x] = [x,y,0]

        # Fill the central 15x5 grid
        for y in range(9, 14):
            for x in range(4, 19):
                frame[y][x] = [x,y,on]

        # Helper function to calculate circular positions
        def calculate_circle_positions(center_x, center_y, radius, start_angle, end_angle, count):
            positions = []
            for i in range(count):
                angle = math.radians(360 * i / count )
                x = (center_x + radius * math.cos(angle))
                y = (center_y + radius * math.sin(angle))
                if round(x) < 4 or round(x) > 18 or round(y) < 9 or round(y) > 13:
                    positions.append((x, y))
            return positions

        # Center of the circle
        center_x, center_y = 11, 11

        self.rings = [
            [],
            [],
            []
        ]

        # Fill the innermost ring (top and bottom 3 positions)
        for x, y in calculate_circle_positions(center_x, center_y, 4, 0, 360, 12):
            self.innerRing.append(LED(int(x), int(y), self))
            frame[int(y)][int(x)] = [x,y,on]

        # Fill the next ring (top and bottom 9 positions)
        for x, y in calculate_circle_positions(center_x, center_y, 7, 0, 360, 24):
            self.middleRing.append(LED(int(x), int(y), self))
            frame[int(y)][int(x)] = [x,y,on]

        # Fill the outermost ring (full 24 positions)
        for x, y in calculate_circle_positions(center_x, center_y, 11, 0, 360, 24):
            self.outerRing.append(LED(int(x), int(y), self))
            frame[int(y)][int(x)] = [x,y,on]

        innerRing_x_to_pos = {}
        middleRing_x_to_pos = {}
        outerRing_x_to_pos = {}
        for x in range(0, 23):
            for idx, item in enumerate(self.innerRing):
                if item.x == x:
                    if x not in innerRing_x_to_pos:
                        innerRing_x_to_pos[x] = []
                    innerRing_x_to_pos[x].append(idx)
            for idx, item in enumerate(self.middleRing):
                if item.x == x:
                    if x not in middleRing_x_to_pos:
                        middleRing_x_to_pos[x] = []
                    middleRing_x_to_pos[x].append(idx)
            for idx, item in enumerate(self.outerRing):
                if item.x == x:
                    if x not in outerRing_x_to_pos:
                        outerRing_x_to_pos[x] = []
                    outerRing_x_to_pos[x].append(idx)
        
        print(innerRing_x_to_pos)
        print(middleRing_x_to_pos)
        print(outerRing_x_to_pos)
        self.mask = frame

    def toggle_mode(self):
        self.mode += 1
        if(self.mode > MAX_MODE):
            self.mode = 0
        self.update_frame()

    def hue_to_rgb(self, h):
        color = QColor()
        color.setHsv(h, 255, 255)
        return color.rgb() & 0xFFFFFF 

    def update_frame(self):
        frame = [[0] * 23 for _ in range(23)]
        self.current_frame = frame

        if self.mode == 0:
            self.update_frame_sine()
        elif self.mode == 1:
            self.update_frame_wipe()
        self.update() 

    def update_frame_wipe(self):

        # Convert virtual X position to indexes on the rings
        innerX2I = {8: [3], 9: [2], 11: [1, 4], 13: [0, 5]}
        middleX2I = {4: [8, 9], 6: [7, 10], 7: [6, 11], 9: [5, 12], 10: [13], 11: [4], 12: [3, 14], 14: [2, 15], 15: [1, 16], 17: [0, 17]}
        outerX2I = {0: [11, 12, 13], 1: [10, 14], 3: [9, 15], 5: [8, 16], 8: [7, 17], 10: [18], 11: [6], 13: [5, 19], 16: [4, 20], 18: [3, 21], 20: [2, 22], 21: [1, 23], 22: [0]}

        # how fast it runs (higher=faster)
        speed = 10
        
        # how fast the tails fade out (higher=shorter tails)
        fade = 10

        # total length of the animation (higher = longer delay between restart)
        length = 230*2

        self.tick += speed
        xmax = (self.tick % (length))/10.0

        for x in range(0, 23):
            if x>xmax: 
                blue=0
            else:
                blue = max(0, 255 - int((xmax - x) * fade))                    
            
            x2 = 22-x
            if x2>xmax: 
                red=0
            else:
                red = max(0, 255 - int((xmax - x2) * fade)) << 16

            value = red | blue

            if x in innerX2I:
                for i in innerX2I[x]:
                    self.innerRing[i].setColor(value)

            if x in middleX2I:
                for i in middleX2I[x]:
                    self.middleRing[i].setColor(value)

            if x in outerX2I:
                for i in outerX2I[x]:
                    self.outerRing[i].setColor(value)
            
            if x > 18 or x < 4:
                continue

            for y in range(0, 5):
                self.matrix.setColor(x-4, y, value)

    def update_frame_sine(self):

        # how much things change each frame
        speed = 10
        self.tick += speed
        
        # how tight the curve is
        curve = 40  
        
        # how wide + how smooth the curve is -- if you double the width and half the samples, 
        # looks roughly the same but calculates half as many points
        width = 10
        samples = 10

        # how many twinkles to add
        num_twinkles = 2

        # color of the twinkle
        twinkle = 0xFFFFFF

        colors = [self.hue_to_rgb((self.tick+i*width)%360) for i in range(samples)]        

        # twinkles
        for i in range(0,num_twinkles):
            pos = random.randint(0,100)
            if pos < 6:
                self.innerRing[pos].setColor(twinkle)
            elif pos < 6+18:
                self.middleRing[pos-6].setColor(twinkle)
            elif pos < 6+18+24:
                self.outerRing[pos-6-18].setColor(twinkle)
            else:
                pass # chance for no twinkle

        # sine wave
        for x in range(0, 15):
            for i in range(0, samples):
                y = math.sin(math.radians(x*curve + self.tick+i*width)) * 2 + 2
                self.matrix.setColor(x, round(y), colors[i])
            


    def paintEvent(self, event):
        if self.current_frame is None:
            return

        painter = QPainter(self)
        cell_size = 20  # Size of each "LED" cell
        pad=5
        blk = QColor('black')
        if self.grid == 0:
            gry = blk
        elif self.grid == 1:
            gry = QColor(0x404040)
        elif self.grid == 2:
            gry = QColor(0x909090)

        painter.fillRect(0,0, cell_size*23, cell_size*23, blk)
        for y, row in enumerate(self.current_frame):
            for x, value in enumerate(row):
                # print(x,y,item)
                xx, yy, m = self.mask[y][x]
                value = value & m
                color = QColor(value) if value else blk
                if(value):
                    painter.fillRect(round(xx * cell_size)+pad, round(yy * cell_size)+pad, cell_size-pad*2, cell_size-pad*2, color)
                
                if(m):
                    painter.setPen(gry)
                    painter.drawRect(round(xx * cell_size), round(yy * cell_size), cell_size, cell_size)