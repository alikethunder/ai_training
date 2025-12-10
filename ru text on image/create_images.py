from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
import os

# Load the dictionary file
with open("ru.txt", "r", encoding="utf-8") as file:
    words = file.readlines()

# Get all font files from the fonts folder
fonts_dir = "fonts"
font_files = [f for f in os.listdir(fonts_dir) if f.endswith(('.ttf', '.otf'))]

if not font_files:
    raise FileNotFoundError("No font files found in the fonts directory.")

# Create output directory if it doesn't exist
output_dir = "img"
os.makedirs(output_dir, exist_ok=True)

# Image size
img_width, img_height = 720, 1280

# Function to calculate text size using textbbox
def calculate_text_size(text, font):
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

replacements = {
    "А": "A", "Б": "ß", "В": "B", "Г": "Î", "Д": "ă", "Е": "E", "Ё": "É", "Ж": "ş",
    "З": "3", "И": "ù", "Й": "ü", "К": "K", "Л": "â", "М": "M", "Н": "H", "О": "O",
    "П": "á", "Р": "P", "С": "C", "Т": "T", "У": "Y", "Ф": "ö", "Х": "X", "Ц": "Ü",
    "Ч": "4", "Ш": "##", "Щ": "!!!", "Ъ": "ț", "Ы": "ä", "Ь": "ţ", "Э": "ó",
    "Ю": "ô", "Я": "®"
}

def transliterate(text):
    """Replace Cyrillic letters in text with their transliterated Latin equivalents."""
    for cyrillic, latin in replacements.items():
        text = text.replace(cyrillic, latin)
    return text

# Iterate through the words and create images
for i, word in enumerate(words):
    word = word.strip()  # Remove any extra whitespace or newline characters
    word = word.replace('\n', os.linesep)

    # For each word, create 3 images for each font
    color_schemes = [
        ("white", "black"),   # White text on black background
        ("black", "white"),   # Black text on white background
        ("red", "grey")       # Red text on grey background
    ]

    for font_file in font_files:
        font_path = os.path.join(fonts_dir, font_file)
        font = ImageFont.truetype(font_path, 60)
        
        # Extract font name without extension for filename
        font_name = os.path.splitext(os.path.basename(font_path))[0]

        # Create 3 images for each font
        for text_color, background_color in color_schemes:
            # Create base image with background color
            img = Image.new("RGB", (img_width, img_height), background_color)
            draw = ImageDraw.Draw(img)

            # Calculate text size and position
            text_width, text_height = calculate_text_size(word, font)
            text_x = (img_width - text_width) // 2
            text_y = (img_height - text_height) // 2

            # Create a separate image for text and apply random rotation
            text_img = Image.new("L", (img_width, img_height), 0)  # 'L' mode for grayscale
            text_draw = ImageDraw.Draw(text_img)
           
            # bold
            if (i + 1) % 2 == 0:  # Even word
                text_draw.text((text_x, text_y), word, font=font, fill=255, stroke_width=2, stroke_fill="white")  # White text on black background with bold
            else:
                text_draw.text((text_x, text_y), word, font=font, fill=255)  # White text on black background

            # Apply anti-aliasing during rotation
            rotated_text = text_img.rotate(
                random.uniform(-15, 15),
                resample=Image.Resampling.BICUBIC,  # Anti-aliasing for smooth edges
                expand=True
            )

            # Colorize the rotated text and paste it onto the base image
            colored_text = ImageOps.colorize(rotated_text, black=background_color, white=text_color)
            img.paste(colored_text, (0, 0), rotated_text)

            # Save the image
            filename = f"ru_{i + 1}_{font_name}_{text_color}"
            img.save(os.path.join(output_dir, filename + ".png"))

            # Create and save the .txt file with the specified content
            with open(os.path.join(output_dir, filename + ".txt"), "w", encoding="utf-8") as text_file:
                word_encoded = transliterate(word)
                text_file.write(f"{text_color} text \"{word_encoded}\" on {background_color} background font {font_name}")

            print(f"Created: {filename}")

print("Images and text files created successfully!")