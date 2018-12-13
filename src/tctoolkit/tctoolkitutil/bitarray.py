# -*- encoding: utf-8 -*-
'''
bitarray.py

Really simple bitarray implented using default 'bytearray' class

Copyright (C) 2018 Nitin Bhide (nitinbhide@gmail.com, nitinbhide@thinkingcraftsman.in)

This module is part of Thinking Craftsman Toolkit (TC Toolkit) and is released under the
New BSD License: http://www.opensource.org/licenses/bsd-license.php
TC Toolkit is hosted at https://bitbucket.org/nitinbhide/tctoolkit
'''

from __future__ import unicode_literals
from __future__ import print_function

class BitArray(object):
    '''
    really simple 'bitarray' which provides indexing and manipulating bit values. Uses
    standard Python ByteArray object to store the data
    '''
    def __init__(self, size):
        self.size = size
        self.bytes = bytearray(int(size/8.0+1.0))
    
    def __getitem__(self, index):
        '''
        index is assumed to be integer. not checked.
        '''
        if not (index>=0 and index < self.size):
            raise IndexError
        byteindex = int(index/8)
        bitindex = index % 8
        return (self.bytes[byteindex] & (0x01 << bitindex)) >> bitindex
    
    def __setitem__(self, index, value):
        '''
        value must be 'true' or 'false (i.e. 0 or 1). Not checked
        '''
        assert index>=0 and index < self.size
        assert value == 0 or value == 1
        byteindex = int(index/8)
        bitindex = index % 8
        value = 0x01 & value
        self.bytes[byteindex] = self.bytes[byteindex] | (value << bitindex)
    
    def hex(self):
        '''
        return hex string representation of internal bytearray. (mainly for debugging)
        Will not work with python 2.x
        '''
        return self.bytes.hex()

if __name__ == '__main__':
    #run some simple tests
    bits8 = BitArray(8)
    assert len(bits8.bytes) == 2
    bits5 = BitArray(5)
    assert len(bits5.bytes) == 1
    bits9 = BitArray(9)
    assert len(bits9.bytes) == 2
    bits8[0] = 1
    assert bits8[0] == 1 and bits8[1] == 0
    bits8[3] = 1
    assert bits8[0] == 1 and bits8[3] == 1
    bits9[8] = 1
    assert bits9[8] == 1 and bits9[0] == 0
    
    #simple performance test to set 100000 bits and read them back
    from random import randrange
    from time import time
    start = time()
    size = 100000
    bits = BitArray(size)
    for i in range(0, 100*1000):
        i = randrange(size)
        bits[i] = 1
        assert bits[i] == 1
    end = time()
    #print(bits.hex())
    print(end-start)
    
    