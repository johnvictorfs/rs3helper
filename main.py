from rs3helper.image_reader import generate_rank_images, set_rank_images_backgrounds, look_for_perks, get_application_weapons

if __name__ == "__main__":
    generate_rank_images()
    set_rank_images_backgrounds()

    application_images = get_application_weapons()

    look_for_perks(application_images)
