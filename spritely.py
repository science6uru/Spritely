from wand.image import Image
from wand.drawing import Drawing
import argparse, sys, os, re
from os import walk
from wand.display import display
import plyer
from wand.api import library
import ctypes
import time

'''
Stacks all the image files on top of eachother and calculates the minimum bounding box within the image that captures all the content.
'''
def calculate_trim(images):
    print("calculating trim dimensions")
    with Drawing() as draw:
        draw.alpha_channel = True
        root = images[0].clone()
        print(f"base image size {root.width}x{root.height}")
        for f in images[1:]:
            draw.composite(operator='over', left=0, top=0, width=f.width, height=f.height, image=f.clone())
        draw(root)
        chop_str = root.percent_escape("%@")
        dims, x, y = chop_str.split("+")
        w, h = dims.split("x")
        return {'width':int(w), 'height':int(h), 'left':int(x), 'top':int(y)}

'''
Calculates bounds of all images stacked and crops each image to the results
'''
def trim_images(images, dimensions=None):
    if dimensions is None:
        dimensions = calculate_trim(images)
    print(f"Cropping images to {dimensions}")
    for image in images:
        image.crop(**dimensions)

'''
Resize image without distorting
'''
def smart_resize(image, width, height):
    iw = image.width
    ih = image.height
    wr = width / iw
    hr = height / ih
    ratio = min(wr, hr)
    image.background_color="transparent"
    # print(f"resizing to {min(width,  round(iw*ratio))}x{min(height, round(ih*ratio))}")
    image.resize(min(width,  round(iw*ratio)), min(height, round(ih*ratio)))
    # print(f"setting canvas size to {width}x{height}")
    image.extent(width, height, gravity="center")

'''
Reduces item count by evenly selecting from items
'''
def resample(items, target_count):
    source_count = len(items)
    print(f"Resampling {source_count} images, to {target_count}")
    if source_count < target_count:
        print("Not enough images to resample")
        sys.exit(1)
    skip_ratio = source_count / target_count
    print(f"resampling image sequence with {skip_ratio}:1 ratio")
    indices = [0]+[round(i * skip_ratio) for i in range(1, target_count)]
    return [items[i] for i in indices]

'''
Gets and returns a list of images from a directory
'''
def get_directory_images(directory):
    source_files = [os.path.join(directory, f) for f in next(walk(directory), (None, None, []))[2] if re.search("\.(png|jpg|jpeg|gif|tiff)", f)]
    source_files.sort()
    return [Image(filename=f) for f in source_files]

def images_from_sources(sources):
    if sources is None or len(sources) == 0:
        directory=plyer.filechooser.choose_dir()
        if directory is None:
            sys.exit(0)
        return get_directory_images(directory[0])
    elif len(sources) == 1:
        if not os.path.isdir(sources[0]):
            print("Please select either multiple images or a single directory containing multiple images")
            sys.exit(1)
        return get_directory_images(sources[0])
    else:
        for source in sources:
            if os.path.isdir(source):
                print("Please select either multiple images or a single directory containing multiple images")
                sys.exit(1)
        return [Image(filename=f) for f in sources]
            

def create_animated_gif(images, filename):
    img = Image()
    img.background_color="transparent"
    # Tell python about library method
    library.MagickSetImageDispose.argtypes = [ctypes.c_void_p, # Wand
                                              ctypes.c_int]    # DisposeType
    BackgroundDispose = ctypes.c_int(2)
    for item in images:
        library.MagickSetImageDispose(item.wand, BackgroundDispose)
        img.sequence.append(item)
    img.save(filename=filename)

def create_spritesheet(images, rows, columns, filename):
    img = Image()
    img.background_color="transparent"
    for item in images:
        img.image_add(item)
    img.montage(mode="concatenate", tile=f"{columns}x{rows}")
    img.save(filename=filename)




def action_spritesheet(sources, width, height, rows, columns, out, **kwargs):
    print(kwargs)
    if (width is None or height is None) and (width is not None or height is not None):
        print("You must specify width and height, or neither")
        sys.exit(1)

    images = images_from_sources(sources)

    images = resample(images, rows*columns)

    dimensions = calculate_trim(images)
    resize=True
    if width is None and height is None:
        resize = False
        width = dimensions['width']
        height = dimensions['height']

    trim_images(images, dimensions)
    if resize:
        for image in images:
            smart_resize(image, width, height)
    if out is None:
        selected = plyer.filechooser.save_file()
        if selected is not None:
            out = selected[0]
    if out is not None:
        create_spritesheet(images, rows, columns, out)
 
def action_gif(sources, width, height, frames, out, **kwargs):
    print(kwargs)
    if (width is None or height is None) and (width is not None or height is not None):
        print("You must specify width and height, or neither")
        sys.exit(1)

    images = images_from_sources(sources)

    if frames is None:
        frames = len(sources)
    else:
        images = resample(images, frames)

    dimensions = calculate_trim(images)
    resize=True
    if width is None and height is None:
        resize = False
        width = dimensions['width']
        height = dimensions['height']

    trim_images(images, dimensions)
    if resize:
        for image in images:
            smart_resize(image, width, height)
    if out is None:
        selected = plyer.filechooser.save_file()
        if selected is not None:
            out = selected[0]
    if out is not None:
        create_animated_gif(images, out)
    
def action_flipbook(sources, size, out, **kwargs):
    s = round(1024 / size)
    action_spritesheet(sources, s, s, size, size, out)



def main():
    parser = argparse.ArgumentParser(prog='spritely', description='Create spritesheets from images.', conflict_handler='resolve')
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--out', help="Name for the output file")
    common.add_argument("sources", nargs="*", help="Directory or list of images to be used as the source")

    sub_parser = parser.add_subparsers()
    ss = sub_parser.add_parser("spritesheet", parents=[common], help="Create custom format spritesheets for animations", conflict_handler='resolve')
    ss.set_defaults(func=action_spritesheet)
    gif = sub_parser.add_parser("gif", parents=[common], help="Create animated GIF from inputs")
    gif.set_defaults(func=action_gif)
    rb = sub_parser.add_parser("flipbook", parents=[common], help="Create spritesheets that are compatible with Roblox")
    rb.set_defaults(func=action_flipbook)

    gif.add_argument('--frames', type=int, help="Count of frames for animated gif. Defaults to count of inputs")
    specific_sizing = gif.add_argument_group()
    specific_sizing.add_argument('--width', type=int, help="Width of the animated gif")
    specific_sizing.add_argument('--height', type=int, help="Height of the animated gif")
    # gif.add_argument('--out', help="Name for the output file")

    manual_formats = ss.add_argument_group()
    manual_formats.add_argument('--rows', type=int, required=True, help="Number of rows of spritesheet images.")
    manual_formats.add_argument('--columns', type=int, required=True, help="Number of columns of spritesheet images.")
    specific_sizing = ss.add_argument_group()
    specific_sizing.add_argument('--width', type=int, help="Width of the animated sprite (width of each 'thumbnail image')")
    specific_sizing.add_argument('--height', type=int, help="Height of the animated sprite (height of each 'thumbnail image')")
    # ss.add_argument('--out', help="Name for the output file")

    rb.add_argument("--size", choices=[2, 4, 8], type=int, help="2x2, 4x4 or 8x8 roblox-compatibleformat")
    args = parser.parse_args()

    # print(args)
    if 'func' in args.__dict__ is not None:
        args.func(**args.__dict__)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
  main()