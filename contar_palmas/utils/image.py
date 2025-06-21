from typing import Literal
from pathlib import Path

import PIL
import tifffile
import numpy as np
import typer
from PIL import Image as pil_img
from PIL.Image.core import PixelAccess
from loguru import logger as log

app = typer.Typer()


def load_image(
    input_image_path: Path,
    memmap: bool,
    lib: Literal["tifffile", "pil"]
) -> PIL.Image.Image:
    try:
        if lib == "tifffile":
            if memmap:
                img_arr = tifffile.memmap(str(input_image_path))
            else:
                img_arr = tifffile.imread(str(input_image_path))

            log.info(f"Opened with tifffile (memmap={memmap}): {img_arr.shape=}")
            return img_arr  # TODO: provide PixelAccess interface

        elif lib == "pil":
            img = pil_img.open(str(input_image_path))
            return img
        # Access a portion of the image data (e.g., a slice)
        # Work with the image slice (it will be loaded into memory as needed)

    except FileNotFoundError:
        log.error("The specified TIFF file was not found")
    except Exception as e:
        log.exception(f"An exception occurred", exc_info=e)

    finally:
        # Close the memmap object to release the file handle
        if 'img_arr' in locals():
            del img_arr


@app.command("tile")
def tile(
    input_image_path: Path,
    lib: str = typer.Option("tifffile", help="Possible values: tifffile, pillow"),
    tile_width: int = typer.Option(672, help="Width of the tile"),
    tile_height: int = typer.Option(448, help="Height of the tile"),
    memmap: bool = typer.Option(
        False,
        help="Whether to use memmap when opening image (i.e. avoid loading whole image to memory)"
    ),
) -> None:
    # Open the TIFF file using memmap

    assert lib in ("tifffile", "pil"), f"{lib=} is not a valid value"
    lib: Literal["tifffile", "pil"]
    img = load_image(input_image_path, memmap=memmap, lib=lib)

    tiles_dir = input_image_path.with_suffix(".tiles")
    tiles_dir.mkdir(parents=True, exist_ok=True)

    width, height = img.size
    y_offsets = [0] + sorted(np.arange(height, 0, -tile_height).tolist())[:-1]
    x_offsets = [0] + sorted(np.arange(width, 0, -tile_width).tolist())[:-1]

    for i in range(len(y_offsets)):
        for j in range(len(x_offsets)):
            x_offset = x_offsets[j]
            y_offset = y_offsets[i]

            file_name = f"{i:02d}-{j:02d}-yoffset-{y_offset:05d}-xoffset-{x_offset:05d}-h{tile_height}-w{tile_width}.png"
            file_path = tiles_dir / file_name
            tile = img.crop((x_offset, y_offset, x_offset + tile_width, y_offset + tile_height))

            if is_non_empty(tile):
                log.info(f"Outputing tile to: {file_name}")
                tile.save(file_path)
            else:
                log.info(f"Image is empty (all pixels are black), not producing tile")
                continue


def is_non_empty(tile: pil_img.Image) -> bool:
    img_hsv = tile.convert("HSV")
    value_chan = np.array(img_hsv)[:, :, 2]
    min_value, max_value = np.min(value_chan), np.max(value_chan)
    if min_value == 0 and max_value == 0:
        return False  # all black pixels -> empty image
    else:
        return True
