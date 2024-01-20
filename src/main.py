import json
from math import ceil
import math
import os
from typing import Callable, Dict, List, Sequence, Tuple, TypeVar
from PIL import Image, ImageDraw

T = TypeVar("T")


def load_image(image_path: str) -> Image.Image:
    return Image.open(image_path)


def save_image(img: Image.Image, save_path: str):
    img.save(save_path)


def resize_image_to_square(image: Image.Image, square_size: int):
    return image.resize((square_size, square_size))


def process_raw_source_images(
    raw_source_img_dir: str, processed_source_img_dir: str, square_size: int
):
    if not os.path.isdir(processed_source_img_dir):
        os.makedirs(processed_source_img_dir)

    for source_img_name in os.listdir(raw_source_img_dir):
        source_img: Image.Image = load_image(
            os.path.join(raw_source_img_dir, source_img_name)
        )
        source_img = resize_image_to_square(source_img, square_size)
        save_image(source_img, os.path.join(processed_source_img_dir, source_img_name))


def get_image_data(img: Image.Image) -> Sequence[Tuple[int, int, int]]:
    return img.getdata()


def avg_color(img: Image.Image) -> Tuple[int, int, int]:
    r, g, b = 0, 0, 0
    n_pixels = 0
    for pixel in get_image_data(img):
        r += pixel[0]
        g += pixel[1]
        b += pixel[2]
        n_pixels += 1
    return round(r / n_pixels), round(g / n_pixels), round(b / n_pixels)


def generate_cache(
    source_images_dir: str, cache_file_path: str
) -> Dict[str, Tuple[int, int, int]]:
    cache: Dict[str, Tuple[int, int, int]] = {}

    for source_image_name in os.listdir(source_images_dir):
        source_image_path: str = os.path.join(source_images_dir, source_image_name)
        source_image: Image.Image = load_image(source_image_path)
        cache[source_image_path] = avg_color(source_image)

    with open(cache_file_path, "w+") as f:
        json.dump(cache, f)

    return cache


def get_cache(cache_file_path: str) -> Dict[str, Tuple[int, int, int]] | None:
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as f:
            return json.load(f)


def divide(img: Image.Image, square_size: int) -> List[List[Image.Image]]:
    n_images_in_row = ceil(img.width / square_size)
    n_rows_in_images = ceil(img.height / square_size)
    return [
        [
            img.crop(
                (
                    x * square_size,
                    y * square_size,
                    min((x + 1) * square_size, img.width),
                    min((y + 1) * square_size, img.height),
                )
            )
            for x in range(n_images_in_row)
        ]
        for y in range(n_rows_in_images)
    ]


def op_on_divided_images(
    divided_images: List[List[Image.Image]], img_op: Callable[[Image.Image], T]
) -> List[List[T]]:
    return [
        [img_op(image) for image in images_in_row] for images_in_row in divided_images
    ]


def create_blank_image(width: int, height: int) -> Image.Image:
    return Image.new("RGB", (width, height))


def create_colored_image(width: int, height: int, color) -> Image.Image:
    img: Image.Image = create_blank_image(width, height)
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, height), fill=color)
    return img


def fill_with_avg_color(img: Image.Image) -> Image.Image:
    return create_colored_image(img.width, img.height, avg_color(img))


def join_divided_images(images: List[List[Image.Image]]) -> Image.Image:
    divided_img_width: int = images[0][0].width
    divided_img_height: int = images[0][0].height

    joined_image_width: int = sum([images_in_row[0].height for images_in_row in images])
    joined_image_height: int = sum([image.width for image in images[0]])

    joined_image: Image.Image = create_blank_image(
        joined_image_width, joined_image_height
    )

    for y in range(len(images)):
        for x in range(len(images[y])):
            img: Image.Image = images[y][x]
            joined_image.paste(img, (x * divided_img_width, y * divided_img_height))

    return joined_image


def distance_between_two_pixels(
    p1: Tuple[int, int, int], p2: Tuple[int, int, int]
) -> float:
    return math.dist(p1, p2)


def get_closest_image(
    cache: Dict[str, Tuple[int, int, int]], pixel: Tuple[int, int, int]
):
    return min(
        cache,
        key=lambda image_path: distance_between_two_pixels(cache[image_path], pixel),
    )


if __name__ == "__main__":
    input_img: Image.Image = load_image("input/monkey.jpeg")

    processed_source_images_dir: str = "source/processed"

    # One time script
    # raw_source_images_dir: str = "source/raw"
    # process_raw_source_images(raw_source_images_dir, processed_source_images_dir, 300)

    cache_file_path: str = "source/cache.json"
    cache: Dict[str, Tuple[int, int, int]] | None = get_cache(cache_file_path)
    if cache is None:
        cache = generate_cache(processed_source_images_dir, cache_file_path)

    square_size: int = 20
    divided_images: List[List[Image.Image]] = divide(input_img, square_size)

    divided_images_with_filled_colors: List[List[Image.Image]] = op_on_divided_images(
        divided_images,
        lambda img: resize_image_to_square(
            load_image(get_closest_image(cache, avg_color(img))), 100
        ),
    )

    joined_img: Image.Image = join_divided_images(divided_images_with_filled_colors)

    save_image(joined_img, os.path.join("output", "monkey.jpeg"))
    # joined_img.show()
