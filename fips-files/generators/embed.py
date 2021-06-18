'''
    embed.py

      Convert binary files to a C array in a header.

      Usage:

      Create a YAML file with a list of files to convert and options:

      ---
      options:
          prefix: [optional C name prefix, default is 'embed_']
          src_dir: [optional relative source directory]
          list_items: true [default is false, see below]
      files:
          - c64_basic.bin
          - c64_char.bin
          - c64_kernalv3.bin

      All files will be dumped into a single C header, each file will 
      be dumped into a C array of type 'unsigned char []' and name
      '[prefix][file name]_[file extension]'.

      If the option 'list_items: true' is provided, an array of item descriptions
      and a define with the number of items is provided looking like this, this
      allows to iterate over the embedded data at runtime.

          typedef struct { const char* name; const uint8_t* ptr; int size; } [prefix_]item_t;
          #define [PREFIX_]NUM_ITEMS (265)
          [prefix_]item [prefix_]items[[PREFIX_]NUM_ITEMS] = {
              { "_start", dump__start, 3438 },
              { "adca", dump_adca, 842 },
              ...
          };
      If the option 'list_items: "full"' is provided, the behaviour is simmilar to when
      'list_items: true' is used, but, the "real" filenames will be used in the list.
'''

Version = 6

import sys
import os.path
import yaml
import genutil

#-------------------------------------------------------------------------------
def get_file_path(filename, src_dir, file_path) :
    '''
    Returns absolute path to an input file, given file name and 
    another full file path in the same directory.
    '''
    return '{}/{}{}'.format(os.path.dirname(file_path), src_dir, filename)

#-------------------------------------------------------------------------------
def get_file_cname(filename, prefix) :
    return '{}{}'.format(prefix, filename).replace('.','_')

#-------------------------------------------------------------------------------
def gen_header(out_hdr, src_dir, files, prefix, list_items) :
    with open(out_hdr, 'w') as f:
        f.write('#pragma once\n')
        f.write('// #version:{}#\n'.format(Version))
        f.write('// machine generated, do not edit!\n')
        items = {}
        for file in files :
            file_path = get_file_path(file, src_dir, out_hdr)
            print("## embed '{}'".format(file_path))
            if os.path.isfile(file_path) :
                with open(file_path, 'rb') as src_file:
                    file_data = src_file.read()
                    file_cname = get_file_cname(file, prefix)
                    file_size = os.path.getsize(file_path)
                    items[file_cname] = [file, file_size]
                    f.write('unsigned char {}[{}] = {{\n'.format(file_cname, file_size))               
                    num = 0
                    for byte in file_data :
                        if sys.version_info[0] >= 3:
                            f.write(hex(ord(chr(byte))) + ', ')
                        else:
                            f.write(hex(ord(byte)) + ', ')
                        num += 1
                        if 0 == num%16:
                            f.write('\n')
                    f.write('\n};\n')
            else :
                genutil.fmtError("Input file not found: '{}'".format(file_path))
        if list_items:
            f.write('typedef struct {{ const char* name; const uint8_t* ptr; int size; }} {}item_t;\n'.format(prefix))
            f.write('#define {}NUM_ITEMS ({})\n'.format(prefix.upper(), len(items)))
            f.write('{}item_t {}items[{}NUM_ITEMS] = {{\n'.format(prefix, prefix, prefix.upper()))
            for name,item in sorted(items.items()):
                size = item[1]
                text = name[(len(prefix)):]
                if 'full' == list_items:
                    text = item[0]
                f.write('{{ "{}", {}, {} }},\n'.format(text, name, size))
            f.write('};\n')

#-------------------------------------------------------------------------------
def generate(input, out_src, out_hdr) :
    if genutil.isDirty(Version, [input], [out_hdr]) :
        with open(input, 'r') as f :
            desc = yaml.load(f)
        prefix = 'embed_'
        src_dir = ''
        list_items = False
        if 'options' in desc:
            opts = desc['options']
            if 'prefix' in opts:
                prefix = opts['prefix']
            if 'src_dir' in opts:
                src_dir = opts['src_dir'] + '/'
            if 'list_items' in opts:
                list_items = opts['list_items']
        gen_header(out_hdr, src_dir, desc['files'], prefix, list_items)
