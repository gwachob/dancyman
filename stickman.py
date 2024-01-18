import math


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


class Point:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

    x: int = 0
    y: int = 0

    def to_tuple(self) -> (int, int):
        return (self.x, self.y)


class Segment:

    def __init__(self, start:Point, end:Point, length:float, angle:float, z_order: float):
        self.start = start
        self.end = end 
        self.length = length
        self.angle = angle
        self.z_order = z_order

    @classmethod
    def from_point(
        cls,
        start: Point,
        length: float,
        rotation: float,
        z_order: float,
    ):   # Returns Self, but typing module not available on Circuitpython
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

SPINE_SIZE = 63
NECK_SIZE = 20
FACE_SIZE = 20
SHOULDER_SIZE = 23
UPPER_ARM_SIZE = 35
FOREARM_SIZE = 27
HAND_SIZE = 16
HIP_SIZE = 21
THIGH_SIZE = 39
SHIN_SIZE = 43
FOOT_SIZE = 26


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
    def __init__(self):
        self.spine_neck: float = 0  # colinear
        self.neck_head: float = 90.0
        self.neck_left_collar_bone: float = 90.0
        self.left_collar_bone_left_upper_arm: float = 60.0
        self.left_upper_arm_left_forearm: float = 40.0
        self.left_forearm_left_hand: float = -70.0

        self.neck_right_collar_bone: float = -90.0
        self.right_collar_bone_right_upper_arm: float = -60.0
        self.right_upper_arm_right_forearm: float = -40.0
        self.right_forearm_right_hand: float = 70.0

        self.spine_left_hip: float = 90.0  # Hips don't articulate, this should be 180 from spine_right_hip

        self.left_hip_left_thigh: float = 75.0
        self.left_thigh_left_shin: float = 15.0
        self.left_shin_left_foot: float = -90.0

        self.spine_right_hip: float = -90.0
        self.right_hip_right_thigh: float = -75.0
        self.right_thigh_right_shin: float = -15.0
        self.right_shin_right_foot: float = 90.0
        


class Body:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scale_factor = (height / 3) / SPINE_SIZE
        self.segments: list[Segments] = []
        self.center = (width / 2, height / 3)
        self.spine_size = SPINE_SIZE * self.scale_factor
        self.neck_size = NECK_SIZE * self.scale_factor
        self.face_size = FACE_SIZE * self.scale_factor
        self.shoulder_size = SHOULDER_SIZE * self.scale_factor
        self.upper_arm_size = UPPER_ARM_SIZE * self.scale_factor
        self.forearm_size = FOREARM_SIZE * self.scale_factor
        self.hand_size = HAND_SIZE * self.scale_factor
        self.hip_size = HIP_SIZE * self.scale_factor
        self.thigh_size = THIGH_SIZE * self.scale_factor
        self.shin_size = SHIN_SIZE * self.scale_factor
        self.foot_size = FOOT_SIZE * self.scale_factor

    def update_params(self, params: BodyParams):
        """Updates the segments"""
        self.segments = []

        # Order of calculation: Spine Neck Face Shoulders Upper Arm Fore Arm Hand Hips Thighs Shins Feet

        #        neck_bottom = Joint(CENTER[0], int(CENTER[1] - SPINE_SIZE/2))
        #        hip = Joint(CENTER[0], int(CENTER[1] + SPINE_SIZE/2))
        spine = Segment(
            Point(self.center[0], int(self.center[1] - self.spine_size / 2)),
            Point(self.center[0], int(self.center[1] + self.spine_size / 2)),
            self.spine_size,
            0,
            0,
        )
        self.segments.append(spine)

        neck = Segment.from_point(spine.start, self.neck_size, params.spine_neck, 0)
        self.segments.append(neck)

        face = Segment.from_point(
            neck.end, self.face_size, neck.angle + params.neck_head, 0
        )
        self.segments.append(face)

        left_collar_bone = Segment.from_point(
            spine.start,
            self.shoulder_size,
            neck.angle + params.neck_left_collar_bone,
            0,
        )
        self.segments.append(left_collar_bone)

        left_upper_arm = Segment.from_point(
            left_collar_bone.end,
            self.upper_arm_size,
            left_collar_bone.angle + params.left_collar_bone_left_upper_arm,
            0,
        )
        self.segments.append(left_upper_arm)

        left_forearm = Segment.from_point(
            left_upper_arm.end,
            self.forearm_size,
            left_upper_arm.angle + params.left_upper_arm_left_forearm,
            0,
        )
        self.segments.append(left_forearm)

        left_hand = Segment.from_point(
            left_forearm.end,
            self.hand_size,
            left_forearm.angle + params.left_forearm_left_hand,
            0,
        )
        self.segments.append(left_hand)

        right_collar_bone = Segment.from_point(
            spine.start,
            self.shoulder_size,
            neck.angle + params.neck_right_collar_bone,
            0,
        )
        self.segments.append(right_collar_bone)

        right_upper_arm = Segment.from_point(
            right_collar_bone.end,
            self.upper_arm_size,
            right_collar_bone.angle + params.right_collar_bone_right_upper_arm,
            0,
        )
        self.segments.append(right_upper_arm)

        right_forearm = Segment.from_point(
            right_upper_arm.end,
            self.forearm_size,
            right_upper_arm.angle + params.right_upper_arm_right_forearm,
            0,
        )
        self.segments.append(right_forearm)

        right_hand = Segment.from_point(
            right_forearm.end,
            self.hand_size,
            right_forearm.angle + params.right_forearm_right_hand,
            0,
        )
        self.segments.append(right_hand)

        left_hip = Segment.from_point(
            spine.end, self.hip_size, spine.angle + params.spine_left_hip, 0
        )
        self.segments.append(left_hip)

        left_thigh = Segment.from_point(
            left_hip.end,
            self.thigh_size,
            left_hip.angle + params.left_hip_left_thigh,
            0,
        )
        self.segments.append(left_thigh)

        left_shin = Segment.from_point(
            left_thigh.end,
            self.shin_size,
            left_thigh.angle + params.left_thigh_left_shin,
            0,
        )
        self.segments.append(left_shin)

        left_foot = Segment.from_point(
            left_shin.end,
            self.foot_size,
            left_shin.angle + params.left_shin_left_foot,
            0,
        )
        self.segments.append(left_foot)

        right_hip = Segment.from_point(
            spine.end, self.hip_size, spine.angle + params.spine_right_hip, 0
        )
        self.segments.append(right_hip)

        right_thigh = Segment.from_point(
            right_hip.end,
            self.thigh_size,
            right_hip.angle + params.right_hip_right_thigh,
            0,
        )
        self.segments.append(right_thigh)

        right_shin = Segment.from_point(
            right_thigh.end,
            self.shin_size,
            right_thigh.angle + params.right_thigh_right_shin,
            0,
        )
        self.segments.append(right_shin)

        right_foot = Segment.from_point(
            right_shin.end,
            self.foot_size,
            right_shin.angle + params.right_shin_right_foot,
            0,
        )
        self.segments.append(right_foot)

    def get_segments(self) -> list[Segment]:
        return sorted(self.segments, key=lambda segment: segment.z_order)
