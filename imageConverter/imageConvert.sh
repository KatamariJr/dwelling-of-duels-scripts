# accept the first parameter as the image to convert
set -e
args=("$@")

# if help flag is passed, print help message
if [ -z "$args" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: imageConvert.sh <image>"
    echo "Creates modified copies of <image>. One as a jpg, one resized to 250x250 for mp3 tags, and one as a smaller image if the original is larger than 1500x1500"
    exit 0
fi

sourceFile="${args[0]}"


# get the file extension of the arg
ext="${args[0]##*.}"

# get the non-extension part of the arg
filename="${args[0]%.*}"

# get the width and height of the image
width=$(magick identify -format "%w" "$sourceFile")
height=$(magick identify -format "%h" "$sourceFile")

# if the extension is png, create a jpg
if [ "$ext" = "png" ]; then
    magick "$sourceFile" "$filename".jpg
fi

magick "$sourceFile" -resize 250x250^ "$filename"_Small.jpg

# if the image is larger than 1500x1500, write a message and create a smaller image
if [ "$width" -gt 1500 ] || [ "$height" -gt 1500 ]; then
    echo "Image is larger than 1500x1500, creating a smaller image named ${filename}_Resized.jpg"
    echo "You should rename $sourceFile to ${filename}_Large.${ext} and rename ${filename}_Resized.jpg to $sourceFile"
    magick "$sourceFile" -resize 1000x1000^ "$filename"_Resized.jpg
fi