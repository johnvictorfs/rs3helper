import numpy as np
import cv2
import mss


def find_match(image, file_name, text, threshold=0.7):
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
    # bottom_right = (top_left[0] + w, top_left[1] + h)

    for pt in zip(*loc[::-1]):
        # nox_text = cv2.imread('nox_staff_text.png', 1)
        # nox_text = cv2.cvtColor(nox_text, cv2.COLOR_BGR2GRAY)
        try:
            # cv2.imshow('staff', nox_text)
            font = cv2.FONT_HERSHEY_SIMPLEX
            # top_left[1] += 20
            cv2.putText(image, text, top_left, font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            # image[(pt[1] - 25):(pt[1] - 25) + nox_text.shape[0], pt[0]:pt[0] + nox_text.shape[1]] = nox_text
            # cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            # cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        except Exception:
            ...
            # print(e)


def read_quest_thing():
    import subprocess
    from pathlib import Path
    from PIL import Image

    orig = Image.open("test.png")
    orig_pix = orig.load

    new = Image.new(orig.mode, orig.size)
    new_pix = new.load()

    def pixels(img):
        width, height = img.size
        for x in range(width):
            for y in range(height):
                yield x, y

    new.save("out.png")

    subprocess.run("tesseract out.png string", shell=True)
    string = Path('string.txt').read_text()
    print(string.splitlines()[0])


if __name__ == '__main__':
    read_quest_thing()

    import sys
    sys.exit(0)

    with mss.mss() as sct:
        monitor = {"top": 400, "left": 600, "width": 800, "height": 640}
        while True:
            # Get raw pixels from the screen, save it to a Numpy array
            frame = np.array(sct.grab(monitor))
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            find_match(frame, 'nox_staff.png', 'Noxious Staff')
            find_match(frame, 'ovl.png', 'Overload Timer')
            # if not match:
            #     match = find_match(frame, 'nox_staff.png')
            #     if not match:
            #         match = find_match(frame, 'nox_staff.png')
            cv2.imshow('frame', frame)

            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break
