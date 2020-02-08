from PIL import Image
from colorama import Fore
import colorama
import pytesseract
import logging
import cv2

from typing import Optional, Dict, List, Tuple, Union
import os


colorama.init()

logger = logging.getLogger('rs3helper')
logger.setLevel(logging.ERROR)
fileHandler = logging.FileHandler(filename='rs3helper.log', encoding='utf-8')

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
fileHandler.setFormatter(formatter)

stoudtHandler = logging.StreamHandler()
stoudtHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(stoudtHandler)


def read_text(image: Image) -> str:
    resized_image = cv2.resize(image, (0, 0), fx=2, fy=2)
    resized_image = Image.fromarray(resized_image)

    return pytesseract.image_to_string(resized_image, config='--psm 12')


def find_weapon(text: str) -> Optional[str]:
    line: str
    for line in text.split('\n'):
        words = [word for word in line.strip().split(' ') if word.isupper() and 'aprim' not in word.lower()]

        words_joined = ' '.join(words)

        if words_joined.isupper() and len(words_joined) > 8:
            return words_joined.title()
    return None


def find_perk(perk_icon: str, image: Image, threshold=0.55) -> Tuple[bool, float]:
    template_image = cv2.imread(perk_icon, cv2.IMREAD_UNCHANGED)
    template = cv2.cvtColor(template_image, cv2.COLOR_BGR2BGRA)

    edited_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    result = cv2.matchTemplate(edited_image, template, cv2.TM_CCOEFF_NORMED)

    closest = []

    for i in result:
        for j in i:
            if j > 0.40 and 'Precise 5' in perk_icon:
                logger.debug(f"found {j} at threshold {threshold} for {perk_icon}")
            if j > threshold:
                logger.debug(f"match at {j} with threshold {threshold} for {perk_icon}")
                closest.append(j)

    if closest:
        return (True, max(closest))
    return (False, 0)


def trans_paste(bg_img, fg_img, box=(0, 0)):
    fg_img_trans = Image.new("RGBA", bg_img.size)
    fg_img_trans.paste(fg_img, box)
    new_img = Image.alpha_composite(bg_img, fg_img_trans)
    return new_img


def generate_rank_images():
    for perk_file in os.listdir(os.fsencode('images/perks')):
        perk_name = os.fsdecode(perk_file).replace('.png', '').replace('_', ' ').title()
        perk_image = f"images/perks/{os.fsdecode(perk_file)}"
        rank_background = Image.open(perk_image)

        for rank_file in os.listdir(os.fsencode('images/perk_ranks')):
            perk_rank_image = os.fsdecode(rank_file)
            rank_name = perk_rank_image.replace('.png', '')

            rank_image = Image.open(f"images/perk_ranks/{perk_rank_image}")

            merged = trans_paste(rank_background, rank_image)

            merged.save(f'images/perks_with_ranks/{perk_name} {rank_name}.png')


def set_rank_images_backgrounds():
    perk_background = Image.open("images/perk_background.png")

    for rank_file in os.listdir(os.fsencode('images/perks_with_ranks')):
        perk_rank_image = os.fsdecode(rank_file)

        rank_image = Image.open(f"images/perks_with_ranks/{perk_rank_image}")

        merged = trans_paste(perk_background, rank_image)

        merged.save(f'images/perks_with_ranks/{perk_rank_image}')


def get_application_weapons(found_messages=True, not_found_messages=False) -> List[Dict[str, str]]:
    application_images = []

    for application_file in os.listdir(os.fsencode('images/application_images')):
        application_image = f"images/application_images/{os.fsdecode(application_file)}"

        base_image = cv2.imread(application_image, cv2.IMREAD_UNCHANGED)

        weapon_name = find_weapon(read_text(base_image))

        if weapon_name:
            application_images.append({
                'weapon_name': weapon_name,
                'image': base_image
            })

            if found_messages:
                print(Fore.GREEN + f'Found Item: {weapon_name}' + Fore.RESET)
        else:
            if not_found_messages:
                print(Fore.RED + f'Item not found in image: {application_image}' + Fore.RESET)

    return application_images


def look_for_perks(app_images: List[Dict[str, str]]):
    perks: List[Dict[str, Union[str, List[int], int]]] = [
        {'name': 'Aftershock', 'ranks': [1, 2, 3], 'requirement': 3},
        {'name': 'Precise', 'ranks': [1, 2, 3, 4, 5], 'requirement': 5, 'threshold': 0.50},
        {'name': 'Crackling', 'ranks': [1, 2, 3], 'requirement': 3},
        {'name': 'Impatient', 'ranks': [1, 2, 3], 'requirement': 3},
        {'name': 'Enhanced Devoted', 'ranks': [1, 2, 3], 'requirement': 3},
        {'name': 'Biting', 'ranks': [1, 2, 3], 'requirement': 2}
    ]

    for perk in perks:
        assert isinstance(perk['ranks'], list)
        ranks: List[int] = perk['ranks']
        found_perk = False

        for item in app_images:
            highest_threshold = None
            highest_name = None

            rank: int
            for rank in ranks:
                logger.debug(f"Looking for {perk['name']} at rank {rank} in weapon {item['weapon_name']}")
                if perk.get('threshold'):
                    # Use custom matching threshold for Perk, if it exists
                    has_perk, threshold = find_perk(
                        f"images/perks_with_ranks/{perk['name']} {rank}.png",
                        item['image'],
                        threshold=perk['threshold']
                    )
                else:
                    has_perk, threshold = find_perk(f"images/perks_with_ranks/{perk['name']} {rank}.png", item['image'])

                if has_perk and (not highest_threshold or threshold > highest_threshold):
                    found_perk = True
                    assert isinstance(perk['requirement'], int)

                    if rank >= perk['requirement']:
                        highest_name = Fore.GREEN + f"{perk['name']} {rank}" + Fore.RESET
                    else:
                        highest_name = Fore.YELLOW + f"{perk['name']} {rank} (Below Requirement)" + Fore.RESET
                    highest_threshold = threshold

            if highest_name:
                print(Fore.GREEN + f"{item['weapon_name']} has Perk: {highest_name}" + Fore.RESET)

        if not found_perk:
            print(Fore.RED + f"Found no Item with Perk: {perk['name']}" + Fore.RESET)


if __name__ == "__main__":
    print(Fore.BLACK + '___________________________' + Fore.RESET, end='\n')

    application_images = get_application_weapons()

    print('_____________')

    look_for_perks(application_images)

    # found_perks = []
    # for perk_file in os.listdir(os.fsencode('images/perks_with_ranks')):
    #     perk_name = os.fsdecode(perk_file).replace('.png', '').replace('_', ' ').title()
    #     perk_image = f"images/perks_with_ranks/{os.fsdecode(perk_file)}"

    #     for image in application_images:
    #         has_perk, threshold = find_perk(perk_image, image['image'])

    #         if has_perk:
    #             found_perks.append(perk_name.rsplit(' ', 1)[0])
    #             print(Fore.GREEN + f"Item '{image['weapon_name']}' has Perk '{perk_name}'.")

    #     if perk_name.rsplit(' ', 1)[0] not in found_perks:
    #         print(Fore.RED + f"Perk '{perk_name}' was not found in any Weapon/Armour.")
