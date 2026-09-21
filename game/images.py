from PIL import Image
import matplotlib.pyplot as plt
import os


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



if __name__ == '__main__':
    # 1. Load image
    image_path = os.path.join('..', 'assets', 'imgs', 'Vampires1_Walk.png')
    output_path = os.path.join('..', 'assets', 'imgs', 'graphics', 'player')


    image = load_image(image_path)

    # 2. Chop image into tiles
    tile_size = (64, 64)  # width, height
    tiles = chop_image(image, tile_size)

    # 3. Display a particular tile
    row = 0
    col = 0

    show_tile(tiles, row, col)

    # TODO save image 
    save_all_tiles(tiles, output_path)
