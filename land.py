from draw import *
from matrix import *
from display import *

polygons = []
screen = new_screen()
color = [255,255,255]
test_landscape(polygons,0,0,500,500,0,10,5)
draw_polygons(polygons,screen,color)
display(screen)
