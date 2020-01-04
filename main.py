import platform

from PIL import Image
import numpy as np
import pytesseract
import cv2
import mss

import re
from typing import Tuple, Optional


operating_system = platform.system().lower()

if operating_system == "darwin":
    from mss.darwin import MSS
elif operating_system == "linux":
    from mss.linux import MSS
else:
    from mss.windows import MSS


def find_match(image, file_name: str, text: str, threshold: float = 0.7):
    template = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)
    # template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # template = cv2.cvtColor(template, cv2.COLOR_BGR2BGRA)

    # https://stackoverflow.com/a/41647132
    # channels = cv2.split(template)
    # zero_channel = np.zeros_like(channels[0])
    # mask = np.array(channels[3])
    # mask[channels[3] == 0] = 1
    # mask[channels[3] == 100] = 0
    # transparent_mask = cv2.merge([zero_channel, zero_channel, zero_channel, mask])

    cv2.imshow('staff', template)

    # result = cv2.matchTemplate(image, template, cv2.TM_CCORR_NORMED)
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)
    w, h = template.shape[::-1]

    # https://stackoverflow.com/a/51713648
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    bottom_right = (top_left[0] + 95, top_left[1] + 19)

    for pt in zip(*loc[::-1]):
        # nox_text = cv2.imread('nox_staff_text.png', 1)
        # nox_text = cv2.cvtColor(nox_text, cv2.COLOR_BGR2GRAY)
        try:
            # cv2.imshow('staff', nox_text)
            # top_left[1] += 20

            # Add label at match
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # cv2.putText(image, text, top_left, font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            # image[(pt[1] - 25):(pt[1] - 25) + nox_text.shape[0], pt[0]:pt[0] + nox_text.shape[1]] = nox_text
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            # cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        except Exception:
            ...


def find_hp_text(image, file_name: str, text: str, threshold: float = 0.7):
    template = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    _, _, _, (left, upper) = cv2.minMaxLoc(result)

    left += 25
    upper -= 2

    right = left + 75
    lower = upper + 21

    cropped = Image.fromarray(image)

    cropped = cropped.crop((left, upper, right, lower))

    cv2.imshow('cropped', np.array(cropped))

    return cropped


def read_text(image):
    resized_image = cv2.resize(image, (0, 0), fx=2, fy=2)
    resized_image = Image.fromarray(resized_image)
    return pytesseract.image_to_string(resized_image, config='--psm 7')


def format_hp(hp_text: str) -> Optional[Tuple[int, int]]:
    """
    Gets current and max hp from hp bar string, ignoring other characters

    Example:
    '@@ 9900/9900' -> (9900, 9900)
    """
    match = re.search(r"(\d+)/(\d+)", hp_text)

    if match:
        current_hp, max_hp = match.groups()

        return int(current_hp), int(max_hp)
    return None


if __name__ == '__main__':
    sct: MSS
    with mss.mss() as sct:
        monitor = {"top": 400, "left": 600, "width": 800, "height": 640}

        while True:
            # Get raw pixels from the screen, save it to a Numpy array
            frame = np.array(sct.grab(monitor))

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            hp_text = find_hp_text(frame, 'images/hp_icon.png', 'HP Text')
            hp_bar = read_text(np.array(hp_text))

            formatted_hp = format_hp(hp_bar)

            if formatted_hp:
                current_hp, max_hp = formatted_hp

                if current_hp < 9900:
                    import datetime
                    now = datetime.datetime.now()

                    print(f'[DANGER] {now.second} - Current HP at {current_hp}')

            # cv2.imshow('frame', frame)

            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break
