from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import os

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 672


def load_image(image_path):
    """Load an image using a path constructed with os.path.join()."""

    return Image.open(image_path)


def chop_image(image, tile_size):
    """
    Chop an image into tiles of size (tile_width, tile_height).

    Returns:
        tiles: 2D list where tiles[row][col] is a sub-image.
    """
    tile_width, tile_height = tile_size

    image_width, image_height = image.size

    tiles = []

    for y in range(0, image_height, tile_height):
        row = []

        for x in range(0, image_width, tile_width):
            # Coordinates of this tile
            left = x
            upper = y
            right = min(x + tile_width, image_width)
            lower = min(y + tile_height, image_height)

            # Crop the tile
            tile = image.crop((left, upper, right, lower))
            row.append(tile)

        tiles.append(row)

    return tiles


def show_tile(tiles, row, col):
    """Display the tile at the given row and column index."""
    if row < 0 or row >= len(tiles):
        raise IndexError("Row index is out of range.")

    if col < 0 or col >= len(tiles[row]):
        raise IndexError("Column index is out of range.")

    tile = tiles[row][col]
    # plt.style.use('dark_background')
    plt.imshow(tile)
    plt.axis("off")
    plt.title(f"Tile: row={row}, col={col}")
    plt.show()

def save_all_tiles(tiles, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for row, tile_row in enumerate(tiles):
        for col, tile in enumerate(tile_row):
            filename = f"tile_row{row}_col{col}.png"
            output_path = os.path.join(output_dir, filename)

            tile.save(output_path)

    print(f"Saved {sum(len(row) for row in tiles)} tiles to {output_dir}")

def place_icon_with_circular_mask(icon_path, output_path, bg_size, icon_size, position):
    # 1. Create a new black background
    base_image = Image.new("RGB", bg_size, color="black")
    
    # 2. Open and resize the icon
    icon = Image.open(icon_path)
    icon_resized = icon.resize(icon_size, Image.Resampling.LANCZOS)
    
    # 3. Calculate the 20% larger mask size
    mask_w = int(icon_size[0] * 1.2)
    mask_h = int(icon_size[1] * 1.2)
    mask_size = (mask_w, mask_h)
    
    # 4. Create a transparent mask canvas
    mask_layer = Image.new("RGBA", mask_size, color=(0, 0, 0, 0))
    
    # 5. Draw a 20% opaque white circle on the transparent canvas
    # 20% opacity = 51 out of 255
    draw = ImageDraw.Draw(mask_layer)
    draw.ellipse([0, 0, mask_w - 1, mask_h - 1], fill=(255, 255, 255, 51))
    
    # 6. Paste the circular white mask onto the black background
    base_image.paste(mask_layer, position, mask=mask_layer)
    
    # 7. Calculate the centered position for the icon over the circular mask
    offset_x = position[0] + (mask_w - icon_size[0]) // 2
    offset_y = position[1] + (mask_h - icon_size[1]) // 2
    icon_position = (offset_x, offset_y)
    
    # 8. Paste the icon on top of the circle
    if icon_resized.mode in ("RGBA", "LA"):
        base_image.paste(icon_resized, icon_position, mask=icon_resized)
    else:
        base_image.paste(icon_resized, icon_position)
        
    # 9. Save the final photo
    base_image.save(output_path)
    print(f"Saved new image with circular mask to {output_path}")

if __name__ == '__main__':
    # 1. Load image
    image_path = os.path.join('..', 'assets', 'imgs', 'graphics', 'bg', 'imgs', 'Computer01.png')
    output_path = os.path.join('..', 'assets', 'imgs', 'graphics', 'bg', 'imgs', 'computer.png')


    # image = load_image(image_path)

    # 2. Chop image into tiles
    tile_size = (130,125)  # width, height
    # tiles = chop_image(image, tile_size)

    # 3. Display a particular tile
    row = 0
    col = 0

    # for i in range(0, 8, 1):
    #     print(i)
    #     show_tile(tiles, row, i)

    # TODO save image 
    # save_all_tiles(tiles, output_path)

    bg_dimensions = (WINDOW_WIDTH, WINDOW_HEIGHT)      # Width and height of the new background
    new_icon_size = (250, 250)      # Width and height for the resized icon
    width = (WINDOW_WIDTH / 2) - 150
    print(width)
    paste_location = (490, 50)     # (x, y) coordinates for top-left corner of the icon
    
    # place_icon_with_circular_mask(
    #     icon_path=image_path,
    #     output_path=output_path,
    #     bg_size=bg_dimensions,
    #     icon_size=new_icon_size,
    #     position=paste_location
    # )
