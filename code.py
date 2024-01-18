import sys
import time
from stickman import Body, BodyParams
from renderer import Renderer

import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_shapes import line


displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64,
    height=32,
    bit_depth=3,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.D25, board.D24, board.A3, board.A2],
    clock_pin=board.D13,
    latch_pin=board.D0,
    output_enable_pin=board.D1,
    doublebuffer=True,
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

splash = displayio.Group()
display.root_group = splash

FPS = 10
FRAME_TIME = 1 / FPS


class MatrixRenderer(Renderer):
    def __init__(
        self, infile, body: Body, body_params: BodyParams, display: displayio.Display
    ):
        super().__init__(infile, body, body_params)
        self.render_started = None
        self.display = display

    def render_frame(self):
        self.render_started = time.monotonic()
        #print(f"Rendering frame at {self.render_started}")
        new_group = displayio.Group(scale=1)
        self.body.update_params(self.body_params)
        segments = self.body.get_segments()
        display.auto_refresh = False

        for segment in segments:
            new_line = line.Line(
                    x0=int(segment.start.x),
                    y0=int(segment.start.y),
                    x1=int(segment.end.x),
                    y1=int(segment.end.y),
                    color=0xFFFFFF,
                )
            new_group.append(
                new_line
            )
        display.root_group = new_group
        display.refresh(minimum_frames_per_second=0)

    def render_last_frame(self):
        self.render_started = time.monotonic()
        #print(f"Re-rendering frame at {self.render_started}")
        # do nothing here

    def wait_for_frame(self):
        # Probably we should be doing a callback rather than a sleep?
        if self.render_started is None:
            return
        deadline = self.render_started + FRAME_TIME
        wait_time = deadline - time.monotonic()
        if wait_time > 0:
            #print(f"Waiting {wait_time} seconds")
            time.sleep(wait_time)



body = Body(64, 32)
body_params = BodyParams()

while True:
    infile = open("example.anim")
    renderer = MatrixRenderer(infile, body, body_params, display)
    number_frames = renderer.render()
    print(f"Completed rendering with {number_frames} frames")
