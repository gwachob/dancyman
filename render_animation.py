import sys
from stickman import Body, BodyParams
from stickman_pil import make_pil_frame
from renderer import Renderer


class PILRenderer(Renderer):
    def __init__(self, infile, body: Body, body_params: BodyParams):
        super().__init__(infile, body, body_params)
        self.results: [Image] = []

    def render_frame(self):
        self.results.append(make_pil_frame(self.body, self.body_params))

    def render_last_frame(self):
        self.results.append(self.results[-1])

    def write_animated_gif(self, filename: str):
        fps = self.config.get("fps", 10)
        loop = int(self.config.get("loop", 0))
        duration = 1/fps
        print(f"Duration is {duration} and loop is {loop}")
        if len(self.results) > 0:
            self.results[0].save(
                filename, save_all=True, append_images=self.results[1:], duration=duration, loop=loop
            )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        infile = open(sys.argv[1])
    else:
        infile = sys.stdin

    if len(sys.argv) > 2:
        outfilename = sys.argv[2]
    else:
        outfilename = "animation.gif"

    width = 500
    height = 500

    images = []
    body_params = BodyParams()
    body = Body(width, height)
    tween_count = 0

    renderer = PILRenderer(infile, body, body_params)
    renderer.render()
    renderer.write_animated_gif(outfilename)
