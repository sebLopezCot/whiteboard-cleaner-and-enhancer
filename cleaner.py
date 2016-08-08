# Algorithms used in this script were inspired by the following paper
# http://research.microsoft.com/en-us/um/people/zhang/Papers/TR03-39.pdf
# Whiteboard Scanning and Image Enhancement
# by Zhengyou Zhang, Li-wei He
# from June 2003


from PIL import Image
from pylab import *
from numpy import *
from scipy.ndimage import filters
import time
import heapq
import math
import sys

class Timer:
    def __init__(self):
        self.timer = 0

    def start(self):
        self.timer = time.time()

    def getAndReset(self):
        temp = time.time() - self.timer
        self.timer = time.time()
        return temp

timer = Timer()

def lum(pixel):
    R,G,B = pixel
    return 0.2126*R + 0.7152*G + 0.0722*B

def below255(val):
    return 255 if val > 255 else val

timer.start()

print 'Loading image...'

path = sys.argv[1] if len(sys.argv) > 1 else 'board1.jpg'

im = array(Image.open(path).convert("RGB"))

print 'took', timer.getAndReset(), 'seconds.'

print 'Performing setup...'
# image properties
height = len(im)
width = len(im[0])

# calculate the whiteboard image
boxwidth = boxheight = 15
wb_im = array(im)

print 'took', timer.getAndReset(), 'seconds.'

print 'Calculating whiteboard image...'

for rbox in range(0, height/boxheight): # need to add the +1 in later for the pixels that end up not fitting in the box
    for cbox in range(0, width/boxwidth):
        # grab the box of 15 x 15 pixels
        box = [[im[r][c] for c in range(cbox*boxwidth, (cbox+1)*boxwidth)] for r in range(rbox*boxheight, (rbox+1)*boxheight)]

        # store each RGB pixel color in a max heap based on luminosity value and pull out the top 25%
        heap = []
        for y in range(0, boxheight):
            for x in range(0, boxwidth):
                heapq.heappush(heap, (255 - lum(box[y][x]), (box[y][x][0], box[y][x][1], box[y][x][2]) ))

        n = int((boxwidth*boxheight)*0.25)
        topcolors = [heapq.heappop(heap)[1] for i in range(0, n)]

        # average these top 25% colors in RGB
        r = sum([topcolors[i][0] for i in range(0,n)]) / n
        g = sum([topcolors[i][1] for i in range(0,n)]) / n
        b = sum([topcolors[i][2] for i in range(0,n)]) / n

        color_wb = (r,g,b)

        # may be able to reduce time by only saving into a rbox by cbox sized array of color vals
        for r in range(rbox*boxheight, (rbox+1)*boxheight):
            for c in range(cbox*boxwidth, (cbox+1)*boxwidth):
                wb_im[r][c] = color_wb

wb_im_smooth = filters.gaussian_filter(wb_im, 1)

print 'took', timer.getAndReset(), 'seconds.'

""" need to eventually do step 3 which is "Filter the colors of the cells by locally fitting a plane in the RGB
space. Occasionally there are cells that are entirely covered by pen strokes, the cell color computed in
Step 2 is consequently incorrect. Those colors are rejected as outliers by the locally fitted plane and are
replaced by the interpolated values from its neighbors" """

print 'Uniform whitening...'

# make the background uniformly white
for r in range(0, height):
    for c in range(0, width):
        im[r][c] = [min(1.0, im[r][c][n]*1.0/wb_im_smooth[r][c][n])*255 for n in range(0, len(im[r][c]))]

print 'took', timer.getAndReset(), 'seconds.'

print 'Pen saturation...'

# reduce image noise and increase color saturation of the pen strokes
p = 2.0
for r in range(0, height):
    for c in range(0, width):
        im[r][c] = [im[r][c][n] * 0.5 * (1.0 - cos(math.pi * (im[r][c][n]/255.0)**p)) for n in range(0, len(im[r][c]))]

print 'took', timer.getAndReset(), 'seconds.'


imshow(im)

print 'Showing image...'

show()
