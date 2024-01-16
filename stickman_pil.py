import dataclasses
from PIL import Image, ImageDraw
from stickman import Body, BodyParams
from tweener import produce_tweens

BODY_COLOR = (255, 255, 255)


def scale_color(color: (int, int, int), scale: float) -> (int, int, int):
    return (int(color[0] * scale), int(color[1] * scale), int(color[2] * scale))


def make_frame(body: Body, body_params: BodyParams) -> Image:
    frame_image = Image.new("RGB", (body.width, body.height))
    draw = ImageDraw.Draw(frame_image)
    body.update_params(body_params)
    segments = body.get_segments()

    for segment in segments:
        draw.line(
            segment.to_tuples(), fill=scale_color(BODY_COLOR, 1 - segment.z_order)
        )
    return frame_image


def append_frame(frames: [Image], body: Body, body_params: BodyParams):
    frames.append(make_frame(body, body_params))


if __name__ == "__main__":
    images = []
    WIDTH = 500
    HEIGHT = 500
    body_params = BodyParams()
    body = Body(WIDTH, HEIGHT)
    shoulder_start = body_params.neck_left_collar_bone
    elbow_start = body_params.left_upper_arm_left_forearm

    start_position = dataclasses.replace(body_params)
    end_position = dataclasses.replace(body_params)
    end_position.neck_left_collar_bone = shoulder_start - 45
    end_position.left_upper_arm_left_forearm = elbow_start + 45
    end_position.neck_head = 75
    for position in produce_tweens(start_position, end_position, 10):
        append_frame(images, body, position)

    start_position = dataclasses.replace(end_position)
    end_position.neck_left_collar_bone = shoulder_start
    end_position.left_upper_arm_left_forearm = elbow_start
    for position in produce_tweens(start_position, end_position, 10):
        append_frame(images, body, position)

    start_position = dataclasses.replace(end_position)
    end_position.neck_head = 90
    for position in produce_tweens(start_position, end_position, 6):
        append_frame(images, body, position)

    body_params = end_position

    # for anim_angle in range(0, 46, 5):
    #    body_params.neck_left_collar_bone = shoulder_start-anim_angle
    #    body_params.left_upper_arm_left_forearm = elbow_start+anim_angle
    #    append_frame(images, body, body_params)

    # for anim_angle in range(45, -1, -5):
    #    body_params.neck_left_collar_bone = shoulder_start-anim_angle
    #    body_params.left_upper_arm_left_forearm = elbow_start+anim_angle
    #    append_frame(images, body, body_params)

    for repeat in range(3):
        for anim in range(10):
            body_params.spine_neck = -10
            body_params.left_hip_left_thigh = 50
            body_params.right_hip_right_thigh = -50
            append_frame(images, body, body_params)

        for anim in range(10):
            body_params.spine_neck = 10
            body_params.left_hip_left_thigh = 75
            body_params.right_hip_right_thigh = -75
            append_frame(images, body, body_params)

    for anim in range(10, -1, -1):
        body_params.spine_neck = anim
        append_frame(images, body, body_params)

    for repeat in range(10):
        for anim in range(5):
            body_params.left_shin_left_foot = 90
            body_params.right_shin_right_foot = -90
            append_frame(images, body, body_params)
        for anim in range(5):
            body_params.left_shin_left_foot = -90
            body_params.right_shin_right_foot = 90
            append_frame(images, body, body_params)

    images[0].save("splits.gif", save_all=True, append_images=images[1:])
