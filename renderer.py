from stickman import Body, BodyParams
from tweener import produce_tweens

try:
    import copy 
except ImportError:
    import cp_copy as copy


class Renderer:
    def __init__(self, infile, body: Body, body_params: BodyParams):
        self.infile = infile
        self.body = body
        self.body_params = body_params

    def render_frame(self):
        """Return an object that represents a rendered frame."""
        raise NotImplemented

    def render_last_frame(self):
        raise NotImplemented

    def wait_for_frame(self):
        """If you need to render in real time, use this to wait for the next
        time tick. Otherwise ignore this"""
        pass

    def update_params_from_line(self, orig, line):
        params = line.split(",")
        for param in params:
            param = param.strip()
            (name, value) = param.split("=")
            setattr(orig, name, float(value))

    def render(self) -> int:
        count = 0
        for line in self.infile:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            elif line.startswith("*"):
                repetitions = int(line[1:])
                for repeat in range(repetitions):
                    self.wait_for_frame()
                    if count == 0:
                        self.render_frame()
                        count += 1
                    else:
                        self.render_last_frame()
                        count += 1
            elif line.startswith(">"):
                tween_count = int(line[1:])
            else:
                if tween_count > 0:
                    start = copy.deepcopy(self.body_params)
                    end = copy.deepcopy(self.body_params)
                    self.update_params_from_line(end, line)
                    for position in produce_tweens(start, end, tween_count):
                        self.body_params = position
                        self.wait_for_frame()
                        self.render_frame()
                        count += 1
                    self.body_params = end
                    tween_count = 0
                else:
                    self.update_params_from_line(self.body_params, line)
                    self.wait_for_frame()
                    self.render_frame()
                    count += 1
        return count
