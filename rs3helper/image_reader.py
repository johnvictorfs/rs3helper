from PIL import Image
from colorama import Fore, init as colorama_init
import pytesseract
import json
import cv2

from typing import Optional, Dict, List, Tuple, Union
import os

from rs3helper.logger import setup_logger

colorama_init()
logger = setup_logger()


def read_text(image: Image, language: str = 'eng') -> str:
    resized_image = cv2.resize(image, (0, 0), fx=2, fy=2)
    resized_image = Image.fromarray(resized_image)

    return pytesseract.image_to_string(resized_image, config=f' -l {language}')


def find_weapon(text: str) -> Optional[str]:
    logger.info(text)

    line: str
    for line in text.split('\n'):
        if 'apr' not in line.lower() and 'aug' not in line.lower():
            continue

        words = [
            word for word in line.strip().split(' ')
            if word.isupper()
            and len(word) >= 1
            and 'aprim' not in word.lower()
            and 'verificar' not in word.lower()
            and 'check' not in word.lower()
            and '%' not in word.lower()
            and '#' not in word.lower()
            and '_' not in word.lower()
            and '[' not in word.lower()
            and ']' not in word.lower()
            and '\'' not in word.lower()
            and '"' not in word.lower()
        ]

        words_joined = ' '.join(words)

        if words_joined.isupper() and len(words_joined) > 8:
            return words_joined.title().replace(',', '.')
    return None


def find_perk(perk_icon: str, image: Image, threshold=0.45) -> Tuple[bool, float]:
    template_image = cv2.imread(perk_icon, cv2.IMREAD_UNCHANGED)
    template = cv2.cvtColor(template_image, cv2.COLOR_BGR2BGRA)

    edited_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    result = cv2.matchTemplate(edited_image, template, cv2.TM_CCOEFF_NORMED)

    closest = []

    for i in result:
        for j in i:
            if j > threshold:
                logger.info(f"match at {j} with threshold {threshold} for {perk_icon}")
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

            result = f'images/perks_with_ranks/{perk_name} {rank_name}.png'

            merged.save(result)

            logger.info(f'Saved perk to {result}')


def set_rank_images_backgrounds():
    perk_background = Image.open("images/other/perk_background.png")

    for rank_file in os.listdir(os.fsencode('images/perks_with_ranks')):
        perk_rank_image = os.fsdecode(rank_file)

        rank_image = Image.open(f"images/perks_with_ranks/{perk_rank_image}")

        merged = trans_paste(perk_background, rank_image)

        result = f'images/perks_with_ranks/{perk_rank_image}'

        merged.save(result)

        logger.info(f'Set background to {result}')


def get_application_weapons(found_messages=True, not_found_messages=False) -> List[Dict[str, str]]:
    application_images = []

    for application_file in os.listdir(os.fsencode('images/application_images')):
        application_image = f"images/application_images/{os.fsdecode(application_file)}"

        base_image = cv2.imread(application_image, cv2.IMREAD_UNCHANGED)

        weapon_name = find_weapon(read_text(base_image, language='eng'))

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
    with open('rs3helper/perks.json') as f:
        perks: List[Dict[str, Union[str, List[int], int, float]]] = json.load(f)

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
