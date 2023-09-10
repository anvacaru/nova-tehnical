from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Final

import cv2
import numpy as np
import skimage.exposure  # type: ignore
from numpy import ndarray
from PIL import Image  # type: ignore
from pillow_heif import register_heif_opener  # type: ignore

_LOGGER: Final = logging.getLogger(__name__)

LOWER_BOUND_1: Final = np.array([30, 100, 100])
UPPER_BOUND_1: Final = np.array([80, 255, 255])
LOWER_BOUND_2: Final = np.array([36, 25, 25])
UPPER_BOUND_2: Final = np.array([130, 255, 255])


def heic_to_jpg(image_path: Path) -> Path:
    _LOGGER.info(f'Converting {image_path} to jpg.')
    register_heif_opener()
    image = Image.open(image_path)
    stem = image_path.stem
    new_filename = stem + '.jpg'
    new_path = image_path.parent / new_filename
    image.convert('RGB').save(new_path)
    return new_path


def process_image_with_pillow(image_path: Path, output_path: Path) -> None:
    """
    Direct RGBA Manipulation with PIL: Directly checks each pixel's RGB values, making "greenish" pixels transparent using hard-coded boundaries.
    """
    _LOGGER.info(f'Processing {image_path} with Pillow.')
    # Load the image
    img = Image.open(image_path)

    # Ensure it's in RGBA mode (with transparency)
    img = img.convert('RGBA')

    datas = img.getdata()
    new_data = []

    for item in datas:
        if item[0] < 100 and item[1] > 100 and item[2] < 100:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)  # type: ignore
    img.save(output_path, 'PNG')


def process_image_with_opencv_treshold(
    image_path: Path,
    output_path: Path,
) -> None:
    """
    LAB & Thresholding with OpenCV: Detects green by converting to LAB color space, thresholding the A-channel, and refining the resulting mask.
    """
    _LOGGER.info(f'Processing {image_path} with OpenCV, with blur.')

    # load image
    img = cv2.imread(str(image_path))

    # convert to LAB
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    # extract A channel
    A = lab[:, :, 1]

    # threshold A channel
    thresh = cv2.threshold(A, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # blur threshold image
    blur = cv2.GaussianBlur(thresh, (0, 0), sigmaX=5, sigmaY=5, borderType=cv2.BORDER_DEFAULT)

    # stretch so that 255 -> 255 and 127.5 -> 0
    mask = skimage.exposure.rescale_intensity(blur, in_range=(127.5, 255), out_range=(0, 255)).astype(np.uint8)

    # add mask to image as alpha channel
    result = img.copy()
    result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask

    # save output
    cv2.imwrite(str(output_path), result)


def process_image_with_opencv_bounds(
    image_path: Path,
    output_path: Path,
    lbound: ndarray = LOWER_BOUND_1,
    ubound: ndarray = UPPER_BOUND_1,
) -> None:
    """
    H OpenCV: Detects green by converting to LAB color space, thresholding the A-channel, and refining the resulting mask.
    """
    _LOGGER.info(f'Processing {image_path} with OpenCV with green lower and upper bounds')
    _LOGGER.info(f'Green lower bound: {lbound}')
    _LOGGER.info(f'Green upper bound: {ubound}')
    # load image
    img = cv2.imread(str(image_path))

    mask = cv2.inRange(img, lbound, ubound)
    inverse_mask = cv2.bitwise_not(mask)
    result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    result[..., 3] = inverse_mask
    # save output
    cv2.imwrite(str(output_path), result)


def process_image_with_opencv_dominant(image_path: Path, output_path: Path) -> None:
    _LOGGER.info(f'Processing {image_path} with OpenCV with dominant color algorithm')

    img = cv2.imread(str(image_path))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv)

    # get uniques
    unique_colors, counts = np.unique(s, return_counts=True)

    # sort through and grab the most abundant unique color
    big_color = None
    biggest = -1
    for a in range(len(unique_colors)):
        if counts[a] > biggest:
            biggest = counts[a]
            big_color = int(unique_colors[a])

    # get the color mask
    margin = 15
    mask = cv2.inRange(s, big_color - margin, big_color + margin)  # type: ignore

    # smooth out the mask
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.medianBlur(mask, 5)
    mask_inv = cv2.bitwise_not(mask)  # inverse mask

    # Convert image to BGRA format
    img_bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img_bgra[:, :, 3] = mask_inv  # set alpha channel using the inverse mask

    # Save the output as PNG to retain transparency
    cv2.imwrite(str(output_path), img_bgra)


def process_video_with_opencv_bounds(
    input_path: str,
    output_path: str,
    export_to_frames: bool = False,
    lbound: ndarray = LOWER_BOUND_2,
    ubound: ndarray = UPPER_BOUND_2,
) -> None:
    """
    HSV Range Filtering with OpenCV: Targets green by using HSV color space and specifying upper and lower bounds for green hues.
    """
    _LOGGER.info(f'Processing {input_path} with OpenCV with green lower and upper bounds.')
    _LOGGER.info(f'Green lower bound: {lbound}')
    _LOGGER.info(f'Green upper bound: {ubound}')
    if export_to_frames:
        _LOGGER.info(f'Exporting frames to {output_path}')

    video = cv2.VideoCapture(input_path)
    # fourcc = cv2.VideoWriter_fourcc('p', 'n', 'g', ' ')  # type: ignore # Using PNG codec for transparency support
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # type: ignore
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width, height = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if export_to_frames:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        frame_count = 0
    else:
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=True)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        mask = cv2.inRange(frame, lbound, ubound)
        inverse_mask = cv2.bitwise_not(mask)

        rgba_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        rgba_frame[..., 3] = inverse_mask

        if export_to_frames:
            frame_filename = os.path.join(output_path, f'frame_{frame_count:04}.png')
            cv2.imwrite(frame_filename, rgba_frame)
            frame_count += 1
        else:
            out.write(rgba_frame)

    video.release()
    if not export_to_frames:
        out.release()
    cv2.destroyAllWindows()


def process_video_with_opencv_dominant_color(input_path: str, output_path: str, export_to_frames: bool = False) -> None:
    """
    Most Abundant Saturation with OpenCV: egments based on the most dominant saturation level in the image, potentially useful for variable backgrounds.
    """

    _LOGGER.info(f'Processing {input_path} with OpenCV with dominant frames.')
    if export_to_frames:
        _LOGGER.info(f'Exporting frames to {output_path}')
    # open up video
    cap = cv2.VideoCapture(input_path)

    # grab one frame
    scale = 0.5
    _, frame = cap.read()
    h, w = frame.shape[:2]
    h = int(h * scale)
    w = int(w * scale)

    # videowriter
    res = (w, h)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # type: ignore
    if export_to_frames:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        frame_count = 0
    else:
        out = cv2.VideoWriter(output_path, fourcc, 30.0, res)

    # loop
    done = False
    while not done:
        # get frame
        ret, img = cap.read()
        if not ret:
            done = True
            continue

        # resize
        img = cv2.resize(img, res)

        # change to hsv
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # get uniques
        unique_colors, counts = np.unique(s, return_counts=True)

        # sort through and grab the most abundant unique color
        big_color = None
        biggest = -1
        for a in range(len(unique_colors)):
            if counts[a] > biggest:
                biggest = counts[a]
                big_color = int(unique_colors[a])

        # get the color mask
        margin = 15
        mask = cv2.inRange(s, big_color - margin, big_color + margin)  # type: ignore

        # smooth out the mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        mask = cv2.medianBlur(mask, 5)
        mask_inv = cv2.bitwise_not(mask)  # inverse mask

        # Convert image to BGRA format
        img_bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        img_bgra[:, :, 3] = mask_inv  # set alpha channel using the inverse mask

        # save
        if export_to_frames:
            frame_filename = os.path.join(output_path, f'frame_{frame_count:04}.png')
            cv2.imwrite(frame_filename, img_bgra)
            frame_count += 1
        else:
            out.write(img_bgra)

    # close caps
    cap.release()
    if not export_to_frames:
        out.release()
        cv2.destroyAllWindows()
    cv2.destroyAllWindows()


def color_picker(filepath: str) -> None:
    def on_trackbar_change(max_value: int = 255, *_: Any) -> None:
        h_min = cv2.getTrackbarPos('Hue Min', 'Trackbars')
        h_max = cv2.getTrackbarPos('Hue Max', 'Trackbars')
        s_min = cv2.getTrackbarPos('Sat Min', 'Trackbars')
        s_max = cv2.getTrackbarPos('Sat Max', 'Trackbars')
        v_min = cv2.getTrackbarPos('Val Min', 'Trackbars')
        v_max = cv2.getTrackbarPos('Val Max', 'Trackbars')

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow('Mask', mask)
        cv2.imshow('Result', result)

    frame = cv2.imread(filepath)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    cv2.namedWindow('Trackbars')
    cv2.resizeWindow('Trackbars', 640, 240)
    cv2.createTrackbar('Hue Min', 'Trackbars', 0, 179, on_trackbar_change)  # type: ignore
    cv2.createTrackbar('Hue Max', 'Trackbars', 179, 179, on_trackbar_change)  # type: ignore
    cv2.createTrackbar('Sat Min', 'Trackbars', 0, 255, on_trackbar_change)  # type: ignore
    cv2.createTrackbar('Sat Max', 'Trackbars', 255, 255, on_trackbar_change)  # type: ignore
    cv2.createTrackbar('Val Min', 'Trackbars', 0, 255, on_trackbar_change)  # type: ignore
    cv2.createTrackbar('Val Max', 'Trackbars', 255, 255, on_trackbar_change)  # type: ignore

    cv2.imshow('Original', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


h_min = 179
h_max = 0

s_min = 255
s_max = 0

v_min = 255
v_max = 0

TOLERANCE = 20


def color_picker2(filepath: str) -> None:
    # Initialize our min/max values for H, S, and V

    def pick_color(event: int, x: int, y: int, flags: int, param: None) -> None:
        global h_min, h_max, s_min, s_max, v_min, v_max

        if event == cv2.EVENT_LBUTTONDOWN:  # Event check for left mouse button click
            pixel = hsv[y, x]

            # Update the min/max values if the current pixel is outside the previous range
            h_min = min(h_min, pixel[0])
            h_max = max(h_max, pixel[0])

            s_min = min(s_min, pixel[1])
            s_max = max(s_max, pixel[1])

            v_min = min(v_min, pixel[2])
            v_max = max(v_max, pixel[2])

            # Add a tolerance around the selected pixel's HSV value
            lower = np.array([h_min - TOLERANCE, s_min - TOLERANCE, v_min - TOLERANCE])
            upper = np.array([h_max + TOLERANCE, s_max + TOLERANCE, v_max + TOLERANCE])

            mask: np.ndarray = cv2.inRange(hsv, lower, upper)

            # Convert the BGR image to BGRA (with Alpha channel)
            rgba: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

            # Wherever the mask is, set the alpha value to 0 (making it transparent)
            rgba[..., 3] = cv2.bitwise_not(mask)

            print(f'HSV Pixel at ({x}, {y}): H={pixel[0]}, S={pixel[1]}, V={pixel[2]}')
            print(f'Lower Bounds: H={h_min - TOLERANCE}, S={s_min - TOLERANCE}, V={v_min - TOLERANCE}')
            print(f'Upper Bounds: H={h_max + TOLERANCE}, S={s_max + TOLERANCE}, V={v_max + TOLERANCE}')

            # Display the image with transparent areas
            cv2.imshow('Image', rgba)

    # Load the image
    image_path: str = filepath
    image: np.ndarray = cv2.imread(image_path)
    hsv: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create a window and set the callback function to pick_color
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Image', pick_color)  # type: ignore

    # Display the image
    cv2.imshow('Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
