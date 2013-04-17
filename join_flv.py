'''
This is a tool to join two or more FLV files.
How to use:
$ python join_flv.py filename1.flv filename2.flv ...
'''
import os.path
import sys
import struct

timestamp_offset = 0


def has_next_tag(binary_file_object):
    '''
    Check whether file has next tag.
    Parameter type: file object.
    Return: boolean type.
    '''
    if binary_file_object.read(1):
        binary_file_object.seek(-1, 1)
        return True
    return False


def append_first_file(binary_file_object, output_file_object):
    '''
    Append the first file to output file object.
    Parameter type: file object, file object.
    Return: None.
    '''
    output_file_object.write(binary_file_object.read(9 + 4))
    while (has_next_tag(binary_file_object)):
        tag_type = binary_file_object.read(1)
        tag_type_int = struct.unpack('>b', tag_type)[0]
        data_size = binary_file_object.read(3)
        data_size_int = struct.unpack('>i', '\x00' + data_size)[0]
        # Skip script tag.
        if tag_type_int == 18:
            binary_file_object.seek(3 + 1 + 3 + data_size_int + 4, 1)
        # Append audio and video tags.
        else:
            timestamp = binary_file_object.read(3)
            output_file_object.write(tag_type)
            output_file_object.write(data_size)
            output_file_object.write(timestamp)
            output_file_object.write(binary_file_object.read(1 + 3 + data_size_int + 4))
    global timestamp_offset
    timestamp_offset += struct.unpack('>i', '\x00' + timestamp)[0] + 30
    binary_file_object.close()
    return


def append_other_file(binary_file_object, output_file_object):
    '''
    Append the other file to output file object.
    Parameter type: file object, file object.
    Return: None.
    '''
    # Skip file header.
    binary_file_object.seek(9 + 4)
    global timestamp_offset
    while (has_next_tag(binary_file_object)):
        tag_type = binary_file_object.read(1)
        tag_type_int = struct.unpack('>b', tag_type)[0]
        data_size = binary_file_object.read(3)
        data_size_int = struct.unpack('>i', '\x00' + data_size)[0]
        # Skip script tag.
        if tag_type_int == 18:
            binary_file_object.seek(3 + 1 + 3 + data_size_int + 4, 1)
        # Append audio and video tags.
        else:
            timestamp = binary_file_object.read(3)
            new_timestamp = struct.unpack('>i', '\x00' + timestamp)[0] + timestamp_offset
            packed_new_timestamp = struct.pack('>i', new_timestamp)[1:]
            output_file_object.write(tag_type)
            output_file_object.write(data_size)
            output_file_object.write(packed_new_timestamp)
            output_file_object.write(binary_file_object.read(1 + 3 + data_size_int + 4))
    timestamp_offset = new_timestamp + 30
    binary_file_object.close()
    return


def join_flv(output, files):
    '''
    Join all the flv files.
    Parameter type: os path object, a list of os path object.
    Return: None.
    '''
    # Create a new empty output file.
    output_file_object = open(output, 'wb')
    output_file_object.close()
    # Open output file in append mode.
    output_file_object = open(output, 'a+b')
    # Append the first file.
    binary_file_object_1 = open(files[0], 'rb')
    append_first_file(binary_file_object_1, output_file_object)
    # Append the other files.
    for f in files[1:]:
        binary_file_object_2 = open(f, 'rb')
        append_other_file(binary_file_object_2, output_file_object)
    output_file_object.close()
    return


def main():
    input_path_list = [os.path.abspath(path) for path in sys.argv[1:]]
    # Wrong file path.
    for path in input_path_list:
        if not os.path.isfile(path):
            print 'File not exit: ' + path
            return
    dir_path = os.path.dirname(input_path_list[0])
    # Output file is created in the same directory as the first input file.
    output_path = os.path.join(dir_path, 'output.flv')
    join_flv(output_path, input_path_list)
    print 'Succeed!'
    print 'Output file path is ' + output_path
    return


if __name__ == '__main__':
    main()
