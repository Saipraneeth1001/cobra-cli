from PIL import Image

# Define the ASCII characters to represent different shades of gray
ASCII_CHARS = "@%#*+=-:. "

# Resize the image to a smaller width while maintaining the aspect ratio
def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width / 1.65
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

# Normalize pixel values to fit within the ASCII_CHARS range
def normalize_pixel(pixel_value, ascii_chars=ASCII_CHARS):
    num_chars = len(ascii_chars)
    return ascii_chars[pixel_value * (num_chars - 1) // 255]

# Convert each pixel to grayscale and map it to an ASCII character
def image_to_ascii(image, ascii_chars=ASCII_CHARS):
    image = image.convert('L')  # Convert to grayscale
    ascii_str = ''
    pixels = image.getdata()
    for pixel_value in pixels:
        ascii_str += normalize_pixel(pixel_value)
    return ascii_str

# Load the image
image_path = 'cobra2.jpg'
image = Image.open(image_path)

# Resize the image and convert it to ASCII art
resized_image = resize_image(image)
ascii_art = image_to_ascii(resized_image)

# Print the ASCII art
print(ascii_art)

