from PIL import Image, ImageDraw
from dataclasses import dataclass
import numpy as np
import math
import dataclasses
from typing import Self

from tweener import produce_tweens


# Eventually I think we'll want a two pass ordered by Z where we compute the
# locations for each part and then draw the parts in the Z order (back to front)
# but for now we'll draw as we compute
#
# Each function will draw and then return relevant resulting points computed
# based on the thing being drawn and its orientation/position - so each
# connectoin point will be a 3-tuple with (x,y, rotation) where rotation is
# defined as a rotation from vertical
#
# For now, our coordinate system matches PILLOW and is scaled by HEIGHT and WIDTH


@dataclass
class Point:
    x: int = 0
    y: int = 0

    def to_tuple(self) -> (int, int):
        return (self.x, self.y)


@dataclass
class Segment:
    start: Point
    end: Point
    length: float
    angle: float
    z_order: float

    @classmethod
    def from_point(
        cls,
        start: Point,
        length: float,
        rotation: float,
        z_order: float,
    ) -> Self:
        rotation_rad = math.radians(rotation)
        # Lots of fun math
        end_x = start.x + length * math.sin(rotation_rad)
        # 0,0 is upper left, so a "positive" change in the frame of the unit circle/polar coordinates
        # requires subtracting y in this reference frame
        end_y = start.y - length * math.cos(rotation_rad)
        return cls(start, Point(end_x, end_y), length, rotation, z_order)

    #    @classmethod
    #    def from_joint(cls, joint: Joint, z_order: float, length: float, angle: float) -> Segment:
    #        return cls.from_point(joint.to_point(), z_order, length, angle, length)

    def to_tuples(self) -> ((int, int), (int, int)):
        return (self.start.to_tuple(), self.end.to_tuple())


# HARDCODED for now, but possibly these could be params too?

HEIGHT = 500
WIDTH = 500
CENTER = (WIDTH / 2, HEIGHT / 3)
BODY_COLOR = (255, 255, 255)

# 63 is the measurement in cm, we are just scaling to a HEIGHT
# so that 63 is 1/3 the HEIGHT
SCALE_FACTOR = (HEIGHT / 3) / 63
SPINE_SIZE = 63 * SCALE_FACTOR
NECK_SIZE = 20 * SCALE_FACTOR
FACE_SIZE = 20 * SCALE_FACTOR
SHOULDER_SIZE = 23 * SCALE_FACTOR
UPPER_ARM_SIZE = 35 * SCALE_FACTOR
FOREARM_SIZE = 27 * SCALE_FACTOR
HAND_SIZE = 16 * SCALE_FACTOR
HIP_SIZE = 21 * SCALE_FACTOR
THIGH_SIZE = 39 * SCALE_FACTOR
SHIN_SIZE = 43 * SCALE_FACTOR
FOOT_SIZE = 26 * SCALE_FACTOR

def scale_color(color: (int, int, int), scale: float) -> (int, int, int):
    return (int(color[0] * scale),int(color[1] * scale), int(color[2] * scale))
 

@dataclass
class BodyParams:
    """
        Class that contains all the configurations params for all parts of the body.
        Primarily this is a list of angles between segments.
        This gets updated each 'frame' of an animation to define the animation.

    The format is to define the angle between two segments, relative to the
    direction of the segment mentioned first.

    The spine is expected to be the reference, vertical (for now).

    0,0 is in the upper left (image coordinates) and angles are calculated
   need to actually modify the 

    All angles expressed in degrees, clockwise (which may be confusing we
    may need to switch this convention to the polar coordinate system)
    """

    spine_neck: float = 0 # colinear
    neck_head: float = 90.0
    neck_left_collar_bone: float = 90.0
    left_collar_bone_left_upper_arm: float = 60.0
    left_upper_arm_left_forearm: float = 40.0
    left_forearm_left_hand: float = -70.0

    neck_right_collar_bone: float = -90.0
    right_collar_bone_right_upper_arm: float = -60.0
    right_upper_arm_right_forearm: float = -40.0
    right_forearm_right_hand: float = 70.0

    spine_left_hip: float = (
        90.0  # Hips don't articulate, this should be 180 from spine_right_hip
    )

    left_hip_left_thigh: float = 75.0
    left_thigh_left_shin: float = 15.0
    left_shin_left_foot: float = -90.0

    spine_right_hip: float = -90.0
    right_hip_right_thigh: float = -75.0
    right_thigh_right_shin: float = -15.0
    right_shin_right_foot: float = 90.0


class Body:
    def __init__(self):
        self.segments: list[Segments] = []

    def update_params(self, params: BodyParams):
        """Updates the segments"""
        self.segments = []

        # Order of calculation: Spine Neck Face Shoulders Upper Arm Fore Arm Hand Hips Thighs Shins Feet

        #        neck_bottom = Joint(CENTER[0], int(CENTER[1] - SPINE_SIZE/2))
        #        hip = Joint(CENTER[0], int(CENTER[1] + SPINE_SIZE/2))
        spine = Segment(
            Point(CENTER[0], int(CENTER[1] - SPINE_SIZE / 2)),
            Point(CENTER[0], int(CENTER[1] + SPINE_SIZE / 2)),
            SPINE_SIZE,
            0,
            0,
        )
        self.segments.append(spine)

        neck = Segment.from_point(spine.start, NECK_SIZE, params.spine_neck, 0)
        self.segments.append(neck)

        face = Segment.from_point(neck.end, FACE_SIZE, neck.angle + params.neck_head, 0)
        self.segments.append(face)

        left_collar_bone = Segment.from_point(
            spine.start, SHOULDER_SIZE, neck.angle + params.neck_left_collar_bone, 0
        )
        self.segments.append(left_collar_bone)

        left_upper_arm = Segment.from_point(
            left_collar_bone.end,
            UPPER_ARM_SIZE,
            left_collar_bone.angle + params.left_collar_bone_left_upper_arm,
            0,
        )
        self.segments.append(left_upper_arm)

        left_forearm = Segment.from_point(
            left_upper_arm.end,
            FOREARM_SIZE,
            left_upper_arm.angle + params.left_upper_arm_left_forearm,
            0,
        )
        self.segments.append(left_forearm)

        left_hand = Segment.from_point(
            left_forearm.end,
            HAND_SIZE,
            left_forearm.angle + params.left_forearm_left_hand,
            0,
        )
        self.segments.append(left_hand)

        right_collar_bone = Segment.from_point(
            spine.start, SHOULDER_SIZE, neck.angle + params.neck_right_collar_bone, 0
        )
        self.segments.append(right_collar_bone)

        right_upper_arm = Segment.from_point(
            right_collar_bone.end,
            UPPER_ARM_SIZE,
            right_collar_bone.angle + params.right_collar_bone_right_upper_arm,
            0,
        )
        self.segments.append(right_upper_arm)

        right_forearm = Segment.from_point(
            right_upper_arm.end,
            FOREARM_SIZE,
            right_upper_arm.angle + params.right_upper_arm_right_forearm,
            0,
        )
        self.segments.append(right_forearm)

        right_hand = Segment.from_point(
            right_forearm.end,
            HAND_SIZE,
            right_forearm.angle + params.right_forearm_right_hand,
            0,
        )
        self.segments.append(right_hand)


        left_hip = Segment.from_point(
            spine.end, HIP_SIZE, spine.angle + params.spine_left_hip, 0
        )
        self.segments.append(left_hip)

        left_thigh = Segment.from_point(
            left_hip.end,
            THIGH_SIZE,
            left_hip.angle + params.left_hip_left_thigh,
            0,
        )
        self.segments.append(left_thigh)

        left_shin = Segment.from_point(
            left_thigh.end,
            SHIN_SIZE,
            left_thigh.angle + params.left_thigh_left_shin,
            0,
        )
        self.segments.append(left_shin)

        left_foot= Segment.from_point(
            left_shin.end,
            FOOT_SIZE,
            left_shin.angle + params.left_shin_left_foot,
            0,
        )
        self.segments.append(left_foot)

        right_hip = Segment.from_point(
            spine.end, HIP_SIZE, spine.angle + params.spine_right_hip, 0
        )
        self.segments.append(right_hip)

        right_thigh = Segment.from_point(
            right_hip.end,
            THIGH_SIZE,
            right_hip.angle + params.right_hip_right_thigh,
            0,
        )
        self.segments.append(right_thigh)

        right_shin = Segment.from_point(
            right_thigh.end,
            SHIN_SIZE,
            right_thigh.angle + params.right_thigh_right_shin,
            0,
        )
        self.segments.append(right_shin)

        right_foot= Segment.from_point(
            right_shin.end,
            FOOT_SIZE,
            right_shin.angle + params.right_shin_right_foot,
            0,
        )
        self.segments.append(right_foot)


    def get_segments(self) -> list[Segment]:
        return sorted(self.segments, key=lambda segment: segment.z_order)

images = []
body_params = BodyParams()
body = Body()
shoulder_start = body_params.neck_left_collar_bone
elbow_start = body_params.left_upper_arm_left_forearm

def draw_frame(frames, body, body_params):
    frame_image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(frame_image)
    body.update_params(body_params)
    segments = body.get_segments()

    for segment in segments:
        draw.line(segment.to_tuples(), fill=scale_color(BODY_COLOR, 1-segment.z_order))

    frames.append(frame_image)

start_position = dataclasses.replace(body_params)
end_position = dataclasses.replace(body_params)
end_position.neck_left_collar_bone=shoulder_start-45
end_position.left_upper_arm_left_forearm=elbow_start+45
end_position.neck_head = 75
for position in produce_tweens(start_position, end_position, 10):
    draw_frame(images, body, position)

start_position = dataclasses.replace(end_position)
end_position.neck_left_collar_bone=shoulder_start
end_position.left_upper_arm_left_forearm=elbow_start
for position in produce_tweens(start_position, end_position, 10):
    draw_frame(images, body, position)

start_position = dataclasses.replace(end_position)
end_position.neck_head = 90
for position in produce_tweens(start_position, end_position, 6):
    draw_frame(images, body, position)

body_params = end_position

#for anim_angle in range(0, 46, 5):
#    body_params.neck_left_collar_bone = shoulder_start-anim_angle
#    body_params.left_upper_arm_left_forearm = elbow_start+anim_angle
#    draw_frame(images, body, body_params)

#for anim_angle in range(45, -1, -5):
#    body_params.neck_left_collar_bone = shoulder_start-anim_angle
#    body_params.left_upper_arm_left_forearm = elbow_start+anim_angle
#    draw_frame(images, body, body_params)

for repeat in range(3):
    for anim in range(10):
        body_params.spine_neck = -10
        body_params.left_hip_left_thigh = 50
        body_params.right_hip_right_thigh = -50
        draw_frame(images, body, body_params)

    for anim in range(10):
        body_params.spine_neck = 10 
        body_params.left_hip_left_thigh = 75 
        body_params.right_hip_right_thigh = -75
        draw_frame(images, body, body_params)

for anim in range(10, -1, -1):
    body_params.spine_neck = anim
    draw_frame(images, body, body_params)

for repeat in range(10):
    for anim in range(5):
        body_params.left_shin_left_foot = 90
        body_params.right_shin_right_foot = -90
        draw_frame(images, body, body_params)
    for anim in range(5):
        body_params.left_shin_left_foot = -90
        body_params.right_shin_right_foot = 90
        draw_frame(images, body, body_params)

        

images[0].save("splits.gif", save_all=True, append_images=images[1:])
