
from Crypto.Random import random
from Crypto.Hash import SHA512, HMAC

def make_tare_hash(bit, seq, entropy_file=None, custom_hash_func=None):
    if entropy_file:
        raise NotImplementedError("Support for an entropy file is pending.")
    secret = str(random.getrandbits(256))
    return make_wheat_hash(bit, seq, secret, custom_hash_func)

def make_wheat_hash(bit, seq, auth_key, custom_hash_func=None):
    if custom_hash_func:
        return custom_hash_func(str(bit) + str(seq), auth_key)
    h = HMAC.new(auth_key, digestmod=SHA512)
    h.update(str(bit) + str(seq))
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

def compliment_bits(bit_list):
    '''Converts a given list of bits 'bit_list' into its element-wise
    inverse.
    Arguments:
        bit_list : The bits to produce the compliment of.
    Returns:
        A list of bits.'''
    comp = []
    for b in bit_list:
        if b == 0:
            comp.append(1)
        elif b == 1:
            comp.append(0)
        else:
            raise Exception("Bad input found in bit list input: " + `b`)
    return comp

def package_message_to_bits(msg_str, last_seq, auth_key, fake_str="", fake_key=None,
                            custom_hash_func=None, entropy_file=None):
    '''Converts a string to a list of signed bit quartets. Signed bits are a
    message bit (as a character), a sequence number (as a string), and a MAC
    over the message bit and sequence number using a given or preset Hash function.
    Arguments:
        msg_str = the real message to send.
        last_seq = The last sequence number sent out. If this is the first message,
                   it should be a 64-bit nonce.
        auth_key = The actual authentication key to sign the real bits and seq number.
        fake_str = (optional) A red-herring message signed with a fake key.
        fake_key = (optional -- mandatory if fake_str provided) A fake key to sign
                   the fake_str with.
        custom_hash_func = (optional) A custom hash function to perform the signatures
                           with. Helpful if the default hash function of SHA512 is ever
                           broken.
        returns: A list of lists having the following format for its quartets:
                     quartets[0][0] -- msg_bit + seq_number + , + real_MAC
                     quartets[0][1] -- cmp_bit + seq_number + , + random_MAC1
                     quartets[0][2] -- msg_bit + seq_number + , + random_MAC2
                     quartets[0][3] -- cmp_bit + seq_number + , + random_MAC3
                     quartets[1][0] ...
                 There will be one quartet per bit of the message. One of the random_MACs
                 will be a fake_MAC if a fake key and fake string is supplied. The other
                 two will always be using random keys. The order within a quartet is
                 random.'''
    if fake_str and not fake_key:
        raise Exception("No fake key provided to accompany fake string.")
    if fake_key and not fake_str:
        raise Exception("No fake message provided to make use of fake key.")
    
    msg_bits = string_to_bits(msg_str)
    cmp_bits = compliment_bits(msg_bits)
    fake_bits = string_to_bits(fake_str)

    if len(msg_bits) != len(fake_bits) and fake_key:
        raise Exception("Fake message supplied but of different size than real message.")

    # Helps to determine whether to fake_hash the message bit, or its compliment.
    # Would use None for the default case, but want to make a list of the same
    # length, and this seemed simple enough.
    matching_bools = map(lambda a,b: a == b, msg_bits, msg_bits) # All True
    if fake_key:
        matching_bools = map(lambda a,b: a == b, msg_bits, fake_bits)

    quartets = []
    current_seq = last_seq + 1
    for msg_bit, cmp_bit, matching in zip(msg_bits, cmp_bits, matching_bools):
        real_mac = make_wheat_hash(msg_bit, current_seq, auth_key, custom_hash_func)
        comp_mac_A = make_tare_hash(cmp_bit, current_seq, entropy_file, custom_hash_func)

        comp_mac_B = None
        fake_mac = None
        if fake_key:
            if matching:
                fake_mac = make_wheat_hash(msg_bit, current_seq, fake_key, custom_hash_func)
                comp_mac_B = make_tare_hash(cmp_bit, current_seq, entropy_file, custom_hash_func)
            else:
                fake_mac = make_wheat_hash(cmp_bit, current_seq, fake_key, custom_hash_func)
                comp_mac_B = make_tare_hash(msg_bit, current_seq, entropy_file, custom_hash_func)
        else:
            # Just another random MAC then.
            fake_mac = make_tare_hash(msg_bit, current_seq, entropy_file, custom_hash_func)
            comp_mac_B = make_tare_hash(cmp_bit, current_seq, entropy_file, custom_hash_func)
        
        current_quartet = [str(msg_bit) + str(current_seq) + "," + real_mac]
        current_quartet.append(str(cmp_bit) + str(current_seq) + "," + comp_mac_A)
        if matching:
            current_quartet.append(str(msg_bit) + str(current_seq) + "," + fake_mac)
            current_quartet.append(str(cmp_bit) + str(current_seq) + "," + comp_mac_B)
        else:
            current_quartet.append(str(cmp_bit) + str(current_seq) + "," + fake_mac)
            current_quartet.append(str(msg_bit) + str(current_seq) + "," + comp_mac_B)
        
        # Should we support using an entropy file for the shuffling?
        random.shuffle(current_quartet)
        
        quartets.append(current_quartet)
        current_seq += 1
    return quartets    


if __name__ == "__main__":
    print "Testing string to bit-list to string conversion:"
    orig_string = "Hello, my name is Devin"

    bit_list = string_to_bits(orig_string)
    print bit_list

    orig_string = bits_to_string(bit_list)
    print orig_string

    raw_input("Press the ENTER key to continue")
    
    print "\n'Testing' HMAC generation:"
    print "Test 1: " + `make_tare_hash(0, 13)`
    print "Test 2: " + `make_tare_hash(0, 13)`

    print "Testing message packaging in default mode:"
    real_key = "12345678901234567890123456789012"
    real_message = "Hi"
    print "Message being packaged: " + real_message
    print package_message_to_bits(real_message, 10, real_key)

    raw_input("Press the ENTER key to continue")
    
    print "Testing message packaging in duplication mode:"
    fake_key = "09876543210987654321098765432109"
    fake_message = "Me"

    print "Message being packaged: " + real_message
    print "Fake message also being packaged: " + fake_message
    print package_message_to_bits(real_message, 10, real_key,
                                  fake_str=fake_message, fake_key=fake_key)
