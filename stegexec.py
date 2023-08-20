from PIL import Image
import argparse
import os

def encode(script_file: str, image_file: str):
    # Given a path to a Python script and a path to an image, will save
    # script encoded in a steganographic copy of the image to the
    # file path $(image_file)_encoded.png 
    with open(script_file, 'r') as f:
        script = str(f.read())
    print("[*] Script needs an image of at least " + str((len(script) + 1)*8) + ' pixels for it to fit.')
    
    image = Image.open(image_file)
    print('[*] Image is ' + str(image.width) + 'x' + str(image.height) + ' or ' + str(area(image)) + ' pixels.')

    can_fit = isImageBiggerThanMessage(image, script)

    if not can_fit:
        print('[-] Image is too small')
        exit(1)
    
    bin_rep =  asBin(script)
    print(f'[*] Script in binary: \n {bin_rep}')
    print('[*] Now encoding into image...')

    encodeMessage(bin_rep, image)
    print('[+] Script encoded')

    encoded_image = ((image.filename).split(sep='.'))[0] + '_encoded.png'
    print('[*] Saving message as ' + encoded_image)
    saveEncodedImage(image)
    print('[+] Encoded image saved')

def extract(image_path):
    # Given a path to an encoded image, will print encoded script to
    # the command line
    # Note: No checks are, as yet, made to determine if the encoded message is
    # ASCII.

    print('[*] Attempting to read image for script...')
    encoded_image = Image.open(image_path)
    print('[+] Image read OK')
    print('[*] Extracting pixel information...')
    blues = getAllBlue(encoded_image)

    print('[+] Pixel information extracted.')
    print('[*] Decoding script in pixels...')
    blue_as_bin = blueToBin(blues)    

    print('[*] Extracting contents...')
    print(getScript(blue_as_bin))

def run(image_path):
    # Given a path to an encoded image, will execute python code hidden therein

    print('[*] Attempting to read image for script...')
    encoded_image = Image.open(image_path)
    print('[+] Image read OK')
    print('[*] Extracting pixel information...')
    blues = getAllBlue(encoded_image)

    print('[+] Pixel information extracted.')
    print('[*] Decoding script in pixels...')
    blue_as_bin = blueToBin(blues)    

    print('[*] Executing...')
    exec(getScript(blue_as_bin))

    print('[+] Done')

def area(img: Image) -> int:
# Returns area of image
    return img.width*img.height

def binLength(message: str) -> int:
# Returns total bit length of message
# 8 bits per letter, plus 1 bit for coda (NUL symbol for end of message)
    return 8*(len(message) + 1)

def isImageBiggerThanMessage(img: Image, message: str) -> bool:
    return img.width*img.height >= binLength(message)

def binAsDeci(int_deci: int, number_of_figures: int) -> str:
    # Binary representation of a decimal number, set precisely number_of_figures in length
    # Padded with leading zeroes to fit to number_of_figures length
    x = format(int_deci, 'b')
    if len(x) < number_of_figures:
        for i in range(0, number_of_figures - len(x)):
            x = '0' + x
    return x

def asBin(message: str) -> str:
    # Returns list of binary representations of each char in message
    x = []
    for c in message:
        x.append(binAsDeci(ord(c), 8))
    return catElements(x)

def catElements(iter) -> str:
# Returns concatenated elements of interable
    l = ""
    for i in iter:
        l = l + i
    return l

def blueToBin(all_blues: list) -> list:
# Return the 8-bit values within the list of raw all_blues from an image.
# Finding the NUL coda will stop the conversion of int to bin.
    bin_vals = []
    cur = ""
    for i in range(0,len(all_blues)):
        cur += str(all_blues[i]%2)
        if len(cur) == 8:
            bin_vals.append(cur)
            if cur == 8*'0':
                bin_vals.pop()
                return bin_vals
            cur = ""
    return bin_vals

def encodeMessage(bin_message: str, im: Image):
# Observe the following characteristic of an image:
# 1. Given L = len(message), w = width, h = height,
#   message mapped onto image (w,h) fills all points,
#   from (0,0) to (L%w,L//w)

# 2. For position (x,y) in pixel data of image, an index in message
#   is given at (y*w + x)

    if bin_message[-8] != 8*'0':
        bin_message += 8*'0'
    # ensure coda is added

    L = len(bin_message)
    w = im.width
    h = im.height
    x = y = 0
    while (x,y) != (L%w, L//w):
        r = im.getpixel((x,y))[0]
        g = im.getpixel((x,y))[1]
        b = im.getpixel((x,y))[2]
        # get all pixel data
        # pixel data is at point (x,y)

        message_index = bin_message[y*w + x]
        # index in message is (y*w + x)

        # set bits into pixels here
        if int(message_index) == 0 and b % 2 == 1:
            im.putpixel((x,y), (r, g, b-1))
        elif int(message_index) == 1 and b % 2 == 0:
            im.putpixel((x,y), (r, g, b+1))
        x += 1
        if x % w == 0:
            y += 1
            x = 0

def saveEncodedImage(image: Image):
# Save image as PNG
    filename = ((image.filename).split(sep='.'))[0]
    image.save(filename + '_encoded.png')


def getAllBlue(im: Image) -> list:
# Return all blue pixel value information
    blues = []
    w = im.width
    h = im.height
    for y in range(0,h):
        for x in range(0,w):
            blues.append(im.getpixel((x,y))[2])
    return blues

def blueToBin(all_blues: list) -> list:
# Return the 8-bit values within the list of raw all_blues from an image.
# Finding the NUL coda will stop the conversion of int to bin.
    bin_vals = []
    cur = ""
    for i in range(0,len(all_blues)):
        cur += str(all_blues[i]%2)
        if len(cur) == 8:
            bin_vals.append(cur)
            if cur == 8*'0':
                bin_vals.pop()
                return bin_vals
            cur = ""
    return bin_vals

def getScript(encoded_message_list):
    s = ''
    for i in encoded_message_list:
        s += binToChr(i)
    return s

def binToChr(bin_str: str):
# Returns the ASCII character equivalent of a binary string
    return chr(int(('0b'+ bin_str),2))

def main():

    pa = argparse.ArgumentParser(prog='StegExec', description='Execute python code as images')
    
    pa.add_argument("-e", "--encode", help="set mode to encode (specify png image)", action="store_true")
    pa.add_argument("-f", "--file", help="python script to encode")
    pa.add_argument("-r", "--run", help="set mode to run (specify encoded image)", action="store_true")
    pa.add_argument("-x", "--extract", help="set mode to extract and print encoded contents (specify encoded image)", action="store_true")
    pa.add_argument("image", help="image to manipulate")
    
    args = pa.parse_args()
    
    if not (args.encode or args.run or args.extract):
        print('[-] Please select mode')
        exit(1)
    
    if not (args.encode ^ args.run ^ args.extract):
        print('[-] Please select only one mode')
        exit(1)
    
    if not os.path.exists(args.image):
        print('[-] Image file does not exist')
        exit(1)
    
    if args.encode:
        if not args.file:
            print('[-] Python script not specified')
            exit(1)
        if not os.path.exists(args.file):
            print('[-] Python file does not exist')
            exit(1)
        encode(args.file, args.image)

    if args.run:
        run(args.image)
    
    if args.extract:
        extract(args.image)

if __name__ == '__main__':
    main()