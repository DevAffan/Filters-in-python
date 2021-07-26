import numpy as nump
import cv2
from utils import CFEVideoConf, img_resize
capture = cv2.VideoCapture(0)

fps = 30
path = 'saved-media/filter.mp4'
configure = CFEVideoConf(capture, filepath=path, res='480p')
output = cv2.VideoWriter(path, configure.video_type, fps, configure.dims)


def alpha_channel(frame):
    try:
        frame.shape[3]  # looking for the channel
    except IndexError:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    return frame


def hue_saturation(frame, alpha, beta):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s.fill(199)
    v.fill(255)
    hsv = cv2.merge([h, s, v])

    out = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    frame = alpha_channel(frame)
    out = alpha_channel(out)
    cv2.addWeighted(out, 0.25, frame, 1.0, .23, frame)
    return frame


def color_overlay(frame, intensity=0.5, blue=0, green=0, red=0):
    frame = alpha_channel(frame)
    frame_h, frame_w, frame_c = frame.shape
    sepia_bgra = (blue, green, red, 1)
    overlay = nump.full((frame_h, frame_w, 4), sepia_bgra, dtype='uint8')
    cv2.addWeighted(overlay, intensity, frame, 1.0, 0, frame)
    return frame


def sepia(frame, intensity=0.5):
    frame = alpha_channel(frame)
    frame_h, frame_w, frame_c = frame.shape
    sepia_bgra = (20, 66, 112, 1)
    overlay = nump.full((frame_h, frame_w, 4), sepia_bgra, dtype='uint8')
    cv2.addWeighted(overlay, intensity, frame, 1.0, 0, frame)
    return frame


def alpha_blend(frame_1, frame_2, mask):
    alpha = mask / 255.0
    blended = cv2.convertScaleAbs(frame_1 * (1 - alpha) + frame_2 * alpha)
    return blended


def focus_blur(frame, intensity=0.2):
    frame = alpha_channel(frame)
    frame_h, frame_w, frame_c = frame.shape
    y = int(frame_h / 2)
    x = int(frame_w / 2)

    mask = nump.zeros((frame_h, frame_w, 4), dtype='uint8')
    cv2.circle(mask, (x, y), int(y / 2), (255, 255, 255), -1, cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (21, 21), 11)

    blured = cv2.GaussianBlur(frame, (21, 21), 11)
    blended = alpha_blend(frame, blured, 255 - mask)
    frame = cv2.cvtColor(blended, cv2.COLOR_BGRA2BGR)
    return frame


def portrait(frame):
    cv2.imshow('frame', frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGRA)
    blured = cv2.GaussianBlur(frame, (21, 21), 11)
    blended = alpha_blend(frame, blured, mask)
    frame = cv2.cvtColor(blended, cv2.COLOR_BGRA2BGR)
    return frame


def invert(frame):
    return cv2.bitwise_not(frame)

print("hue saturation filter press: 1\n Sepia filter press: 2 \n color overlay filter press: 3 \n invert filter press: 4 \n Blur filter press: 5 \n Portrait filter press: 6")
d_filter = str(input())

while (True):
    # frames
    ret, frame = capture.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

    if d_filter == "1":
        hue_sat = hue_saturation(frame.copy(), alpha=3, beta=3)
        cv2.imshow('hue_sat', hue_sat)

    elif d_filter == "2":
        do_sepia = sepia(frame.copy(), intensity=.8)
        cv2.imshow('do_sepia', do_sepia)

    elif d_filter == "3":
        do_color_overlay = color_overlay(frame.copy(), intensity=.8, green=231, red=123)
        cv2.imshow('do_color_overlay', do_color_overlay)

    elif d_filter == "4":
        do_invert = invert(frame.copy())
        cv2.imshow('do_invert', do_invert)

    elif d_filter == "5":
        blur_mask = focus_blur(frame.copy())
        cv2.imshow('blur_mask', blur_mask)

    elif d_filter == "6":
        do_portrait = portrait(frame.copy())
        cv2.imshow('do_portrait', do_portrait)
    else:
        print("wrong input")
        break
    if cv2.waitKey(20) & 0xFF == ord('q'):
            break

capture.release()
cv2.destroyAllWindows()
