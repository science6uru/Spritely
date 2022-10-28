from wand.image import Image
from wand.drawing import Drawing
import argparse, sys, os, re
from os import walk
from wand.display import display
import plyer

 
parser = argparse.ArgumentParser(prog='spritely', description='Create spritesheets from images.')

parser.add_argument('--directory',
                    type=str,
                    help='the path to image directory',
                    required=False)
parser.add_argument('--rows', type=int, default=8, help="Number of rows of spritesheet images.")
parser.add_argument('--columns', type=int, default=8, help="Number of columns of spritesheet images.")
parser.add_argument('--width', type=int, default=128, help="Width of the animated sprite (width of each 'thumbnail image')")
parser.add_argument('--height', type=int, default=128, help="Height of the animated sprite (height of each 'thumbnail image')")
parser.add_argument('--out', help="Name for the output file")
    
'''
Stacks all the image files on top of eachother and calculates the minimum bounding box within the image that captures all the content.
'''
def calculate_trim(files):
    print("calculating trim dimensions")
    with Drawing() as draw:
        draw.alpha_channel = True
        root = Image(filename=files[0])
        for f in files[1:]:
            fimg = Image(filename=f).clone()
            draw.composite(operator='over', left=0, top=0, width=fimg.width, height=fimg.height, image=fimg)
        draw(root)
        return root.percent_escape("%@")


def create_sprite_from_directory(directory, rows, columns, width, height, **kwargs):
    if not os.path.isdir(directory):
        print("<path> must be a directory of images")
        print(directory)
        parser.print_usage()
        sys.exit(1)

    source_files = [os.path.join(directory, f) for f in next(walk(directory), (None, None, []))[2] if re.search("\.(png|jpg|jpeg|gif|tiff)", f)]
    source_files.sort()
    source_count = len(source_files)
    target_count = rows * columns
    print(f"Found {source_count} image files, and need {target_count} files to create the sprite")
    if source_count < target_count:
        print("Not enough image files to create sprite")
        sys.exit(1)
    skip_ratio = source_count / target_count
    print(f"resampling image sequence with {skip_ratio}:1 ratio")
    indices = [0]+[round(i * skip_ratio) for i in range(1, target_count)]
    # print(f"using indices {indices}")
    source_files = [source_files[i] for i in indices]
    trim = calculate_trim(source_files)
    dims, x, y = trim.split("+")
    w, h = dims.split("x")
    size = max(int(w), int(h))
    print(f"bounding box of animation is {trim}")
    print(f"resizing to {size}x{size}, then shrinking to {width}x{height} to create spritesheet")
    img = Image()
    img.background_color="transparent"
    for src in source_files:
        with Image(filename=src+f"[{trim}]") as item:
            item.background_color="transparent"
            item.extent(size, size, gravity="center")
            item.resize(width, height)
            img.image_add(item)
    img.montage(mode="concatenate", tile=f"{columns}x{rows}")
    return img

def main():
    args = parser.parse_args()

    if args.directory is None:
        args.directory=plyer.filechooser.choose_dir()
        if args.directory is None:
            sys.exit(0)
        args.directory = args.directory[0]
    if args.out is None:
        args.out = f"{args.directory}_{args.rows}x{args.columns}.png"
    img=create_sprite_from_directory(**args.__dict__)
    print(f"writing output file: {args.out}")
    img.save(filename=args.out)

if __name__ == "__main__":
  main()