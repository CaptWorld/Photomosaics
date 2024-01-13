from math import ceil
from typing import Callable, List, Sequence, Tuple, TypeVar
from PIL import Image, ImageDraw

T = TypeVar("T")


def load_image(image_path: str) -> Image.Image:
    return Image.open(image_path)


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


if __name__ == "__main__":
    source_img: Image.Image = load_image("input/monkey.jpeg")

    square_size: int = 3

    divided_images: List[List[Image.Image]] = divide(source_img, square_size)

    divided_images_with_filled_colors: List[List[Image.Image]] = op_on_divided_images(
        divided_images, fill_with_avg_color
    )

    joined_img: Image.Image = join_divided_images(divided_images_with_filled_colors)

    joined_img.show()
