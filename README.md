# rs3helper

## Setup

- Install dependencies
  - Python dependencies ([`poetry`](https://github.com/python-poetry/poetry))
      ```bash
      poetry install
      ```

  - Other dependencies
    - [`tesseract`](https://github.com/tesseract-ocr/tesseract)
      ```bash
      pacman -S tesseract
      ```

    - Tesseract Language Training data
      ```bash
      # English and Portuguese data
      pacman -S tesseract-data-eng tesseract-data-por
      ```
