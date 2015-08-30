#!/usr/bin/env python
# -*- coding: utf-8 -*
#
# iso9075.py - Python codec for ISO-9075
#
#   Copyright 2011 Jesús Torres <jmtorres@ull.es>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import codecs
import re


# XML NCName validator

def validateNCNameChar(index, char):
    ch = ord(char)
    if (ch == ord('_')                     or
       (ch >= ord('A') and ch <= ord('Z')) or
       (ch >= ord('a') and ch <= ord('z')) or
       (ch >= 0x000C0  and ch <= 0x000D6)  or
       (ch >= 0x000D8  and ch <= 0x000F6)  or
       (ch >= 0x000F8  and ch <= 0x002FF)  or
       (ch >= 0x00370  and ch <= 0x0037D)  or
       (ch >= 0x0037F  and ch <= 0x01FFF)  or
       (ch >= 0x0200C  and ch <= 0x0200D)  or
       (ch >= 0x02070  and ch <= 0x0218F)  or
       (ch >= 0x02C00  and ch <= 0x02FEF)  or
       (ch >= 0x03001  and ch <= 0x0D7FF)  or
       (ch >= 0x0F900  and ch <= 0x0FDCF)  or
       (ch >= 0x0FDF0  and ch <= 0x0FFFD)  or
       (ch >= 0x10000  and ch <= 0xEFFFF)):
        return True
    elif not index == 0:
        if (ch == ord('-')                     or
            ch == ord('.')                     or
            ch == 0xB7                         or
           (ch >= ord('0') and ch <= ord('9')) or
           (ch >= 0x0300   and ch <= 0x036F)   or
           (ch >= 0x203F   and ch <= 0x2040)):
            return True
    return False


# Codec API

class Codec(codecs.Codec):

    def encode(self, input, errors='strict', validate=validateNCNameChar):
        return encode(input, errors, validate)

    def decode(self, input, errors='strict'):
        return decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def __init__(self, errors='strict', validate=validateNCNameChar):
        self.lastIndex = 0
        self.validate = validate
        super(IncrementalEncoder, self).__init__(errors)

    def encode(self, input, final=False):
        def validate(index, char):
            self.validate(self.lastIndex + index, char)
    
        output = encode(input, self.errors, validate)
        self.lastIndex += output[1]
        return output[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return decode(input, self.errors)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


# Encoding & decoding functions

def encode(input, errors = 'strict', validate=validateNCNameChar):
    output = unicode()
    input = unicode(input)

    for i in range(len(input)):
        if validate(i, input[i]) == False:
            output += "_x%04x_" % ord(input[i])
        elif re.match("_x[0-9a-fA-F]{4}_", input[i:i+7]):
            output += "_x%04x_" % ord('_')
        else:
            output += input[i]

    return (output, len(input))


def decode(input, errors = 'strict'):
    output = unicode()
    input = unicode(input)

    i = 0
    while i < len(input):
        if re.match("_x[0-9a-fA-F]{4}_", input[i:i+7]):
            output += unichr(int(input[i+2:i+6], 16))
            i += 7
        else:
            output += input[i]
            i += 1

    return (output, len(input))


# Register the codec search function

def register(encoding, validate):
    """Register a ISO-9075 codec.
    
    The codec is registered using the name given in encoding. It will use the
    the function specified in validate to check the characters that must not be
    encoded.
    """
    def find_codec(name):
        if name == encoding:
            return codecs.CodecInfo(
                name=encoding,
                encode=lambda input, errors='strict':
                    Codec().encode(input, errors, validate),
                decode=Codec().decode,
                incrementalencoder=lambda errors='strict':
                    IncrementalEncoder(errors, validate),
                incrementaldecoder=IncrementalDecoder,
                streamreader=StreamReader,
                streamwriter=StreamWriter,
            )
        else:
            return None
    codecs.register(find_codec)

register('iso9075', validateNCNameChar)


if __name__ == '__main__':
    
    import sys
    for line in sys.stdin.readlines():
    	if line[-1] == '\n':
            print unicode(line[:-1], 'utf-8').encode('iso9075').encode('utf-8')
        else:
            sys.stdout.write(
                unicode(line, 'utf-8').encode('iso9075').encode('utf-8'))
