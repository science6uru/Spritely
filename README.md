<p align="center">
    <a href="https://discord.gg/xVtbCuaGfM">
        <img src="https://img.shields.io/discord/1034604635807285392?label=Discord&logo=Discord&style=for-the-badge"
            alt="chat on Discord"></a>
</p>
<p align="center">
Spritely is a free Python tool to completely automate your spritesheet creation workflow.

# Contents
</p>
<p align="center">
    <a href="https://github.com/science6uru/Spritely#about-and-features">
    About and Features

</p>
<p align="center">
    <a href="https://github.com/science6uru/Spritely#installation-and-setup">
    Installation and Setup
        
</p>
<p align="center">
    <a href="https://github.com/science6uru/Spritely#usage">
    Usage
        
</p>
<p align="center">
    <a href="https://github.com/science6uru/Spritely#contribute">
    Contribute
</a>

# About and Features
</p>
<p align="center">
Spritely is a free & open-source tool to completely automate your spritesheet creation workflow with just a few commands. 

Features include:

- Recounting folders of images to a usable amount (Evenly spaced)

- Cropping all images in a folder to the max without cutting images / alpha off (crops all images evenly based on combined maximum dimensions)

- Previewing spritesheet as a .GIF File (Not pre-made spritesheets, only prepared ones are supported as of now)

- Arranging a folder of any amount of images into a usable spritesheet (Customizable grid specifications)

- Allows to add padding to a whole image folder
    
- And much more to come...

# Installation and Setup
First, if you haven't already, you will need to install Homebrew & ImageMagick(Required). If you do not need homebrew you can skip ahead to step 2.
<p align="center">
Homebrew installation (Required for Mac)

```sh
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

<p align="center">
ImageMagick & Pip installation (brew)
    
```sh
brew install imagemagick
brew install python
brew unlink python && brew link python
```

<p align="center">
Spritely installation 

```sh
gh repo clone science6uru/Spritely
```
# Usage
run spritely --help
    
