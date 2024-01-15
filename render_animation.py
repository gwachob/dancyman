import sys
from make_dance import make_frame, Body, BodyParams
from tweener import produce_tweens
import dataclasses

def update_params_from_line(body_params, line):
    params = line.split(",")
    for param in params:
        param = param.strip()
        (name,value) = param.split('=')
        setattr(body_params, name, float(value))
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        infile = open(sys.argv[1])
    else:
        infile = sys.stdin

    WIDTH = 500
    HEIGHT = 500

    images = []
    body_params = BodyParams()
    body = Body(WIDTH, HEIGHT)
    tween_count = 0

    for line in infile:
        line = line.strip()
        if line.startswith("#") or line=="":
            continue
        elif line.startswith("*"):
            repetitions = int(line[1:])
            if len(images) == 0:
                frame_to_copy = make_frame(body, body_params)
            else:
                frame_to_copy = images[-1]

            # Not adding multiple copies, just multiple references to the same frame
            images.extend([frame_to_copy] * repetitions)
        elif line.startswith(">"):
            tween_count = int(line[1:])
        else:
            if (tween_count > 0):
                start = dataclasses.replace(body_params)
            update_params_from_line(body_params, line)
            if (tween_count > 0):
                for position in produce_tweens(start, body_params, tween_count):
                    images.append(make_frame(body, position))
                body_params = position 
                tween_count = 0    
            else:
                images.append(make_frame(body, body_params))
    if len(images) > 0:
        images[0].save("animation.gif", save_all=True, append_images=images[1:])
        
            
       

    


    


