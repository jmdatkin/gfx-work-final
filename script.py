
import mdl, sys
from display import *
from matrix import *
from draw import *

num_frames = 1
basename = "frame"

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    framesdef = "frames" in [c[0] for c in commands]
    basenamedef = "basename" in [c[0] for c in commands]
    varydef = "vary" in [c[0] for c in commands]
    if not framesdef and not basenamedef and not varydef:
        return False
    if varydef and not framesdef:
        print "Found knob definition w/o frame initialization, exiting..."
        sys.exit()
    if framesdef:
        global num_frames, basename
        num_frames = [c[1] for c in commands if c[0] == "frames"][-1]
        basename = [c[1] for c in commands if c[0] == "basename"][-1] if basenamedef else "frame"
        print "Num frames: %d\nFrame prefix: %s" % (num_frames,basename)
    return True
    


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
        
def second_pass( commands, num_frames ):
    knobs = [cmd for cmd in commands if cmd[0]=="vary"]
    knobVals = [{} for i in range(num_frames)]
    for i in range(num_frames):
        for j in knobs:
            if i >= j[2] and i <= j[3]:
                knobVals[i][j[1]] = (i - j[2])*(j[5]-j[4])/(float(j[3])-j[2]) + j[4]
    return knobVals


def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.05
    anim = False
    if first_pass(commands):
        anim = True
    knobVals = second_pass(commands,num_frames)
    for i in range(num_frames):
        if anim:
            for k in knobVals[i]:
                symbols[k][1] = knobVals[i][k]
        clear_screen(screen)
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        for command in commands:
            c = command[0]
            args = command[1:]
            
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                kn = symbols[args[3]][1] if args[3] else 1
                tmp = make_translate(args[0]*kn, args[1]*kn, args[2]*kn)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                kn = symbols[args[3]][1] if args[3] else 1
                tmp = make_scale(args[0]*kn, args[1]*kn, args[2]*kn)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                kn = symbols[args[2]][1] if args[2] else 1
                if args[0] == 'x':
                    tmp = make_rotX(theta*kn)
                elif args[0] == 'y':
                    tmp = make_rotY(theta*kn)
                else:
                    tmp = make_rotZ(theta*kn)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'set':
                symbols[args[0]][1] = float(args[1])
            elif c == 'set_knobs':
                for k in symbols:
                    symbols[k][1] = args[0]
            elif c == 'display':
                if not anim:
                    display(screen)
            elif c == 'save':
                if not anim:
                    save_extension(screen, args[0])
        if anim:
            filename = "%s%03d.png" % (basename, i)#"0"*(max(0,3-len(str(i))))+str(i)+".png")
            print "Saving frame %d as '%s':" % (i,filename)
            for symbol in symbols:
                print "\tKnob: %s\tVal: %f" % (symbol,symbols[symbol][1])
            save_extension(screen,"anim/%s" % filename)
    if anim:
        make_animation(basename)
