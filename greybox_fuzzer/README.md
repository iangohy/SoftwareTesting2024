In python 3 all unicode, python str is either ascii all unicode

COAP:
-fuzz the
HTTP:
-fuzz the post payload
If "Content-Type" isn’t assigned, a browser must process messages as if they were in ISO-8859-1. A browser shouldn't try to guess the encoding, and it certainly shouldn’t ignore "Content-Type". So, if we transfer UTF-8 messages, but do not assign encoding in headers, they will be read as if they were encoded with ISO-8859-1.
https://www.jmix.io/blog/utf-8-in-http-headers/

Side Notes:

Fastest Way to replace a char in a string python: https://stackoverflow.com/questions/1228299/changing-a-character-in-a-string/1228327#1228327

Notes:
UTF Format
1 byte: 0b0xxxxxxx

2 byte: 0b110xxxxx 0b10xxxxxx

3 byte: 0b1110xxxx 0b10xxxxxx 0b10xxxxxx

4 byte: 0b11110xxx 0b10xxxxxx 0b10xxxxxx 0b10xxxxxx
