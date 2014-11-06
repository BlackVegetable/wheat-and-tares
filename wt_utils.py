
from Crypto.Random import random
from Crypto.Hash import SHA512

def make_tare_hash(entropy_file=None):
    if entropy_file:
        raise NotImplementedError("Support for an entropy file is pending.")
    h = SHA512.new()
    h.update(str(random.getrandbits(256)))
    return h.hexdigest()

def string_to_bits(s):
    '''Converts a given string 's' composed of ASCII characters 
    to an ordered list of the bits composing the string.
    Arguments:
        s : The string to convert to a list of bits
    Returns:
        A list of bits.'''
    bit_list = []
    bits_in_character = 8 # 1 byte
    for c in s:
        number_value = ord(c)
        for pos in range(bits_in_character):
            bit_list.append(number_value & 1)
            number_value = number_value >> 1
    return bit_list

def bits_to_string(bit_list):
    '''Converts a given list of bits 'bit_list' to an ASCII
    string.
    Arguments:
        bit_list : The bits to convert to a string
    Returns:
        An ASCII string.'''
    s = ""
    if len(bit_list) % 8 != 0:
        raise Exception("Bit list contains invalid number of bits.")
    number_value = 0
    for bit_pos in range(len(bit_list)):
        number_value += bit_list[bit_pos] << (bit_pos % 8)
        if bit_pos % 8 == 7:
            s += chr(number_value)
            number_value = 0
    return s


if __name__ == "__main__":
    print "Testing string to bit-list to string conversion:"
    orig_string = "Hello, my name is Devin"

    bit_list = string_to_bits(orig_string)
    print bit_list

    orig_string = bits_to_string(bit_list)
    print orig_string

    print "\n'Testing' HMAC generation:"
    print "Test 1: " + `make_tare_hash()`
    print "Test 2: " + `make_tare_hash()`
