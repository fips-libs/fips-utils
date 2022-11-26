'''
    Copy files from project directory into the deployment directory.

    Usage:

    Create a YAML file with a list of files to copy and (optional)
    options:

    ---
    options:
        src_dir: [optional relative source directory]
        dst_dir: [optional relative destination directory]
        # optional platform-specific overrides
        ios:
            dst_dir:    [optional relative dst_dir for iOS]
        macos:
            dst_dir:    [optional relative dst_dir for macOS]
    files:
        - DroidSansJapanese.ttf
        - DroidSerif-Bold.ttf
        - DroidSerif-Italic.ttf
        - DroidSerif-Regular.ttf

    By default the files are expected in the same directory as the .yml file,
    and are copied to the root of the deploy dir (where the executable is
    located).

    In dst_dir, any $TARGET_NAME will be replaced with the current target name
    as defined in fips_being_*().

    To invoke the copy operation as custom build step from CMakeLists.txt files,
    use the cmake macro from inside a fips_begin_*()/fips_end() block:

    fipsutil_copy(yml_file.yml)

    This macro is defined in fips-utils/fips-files/include.cmake.
'''
Version = 2

import genutil as util
import subprocess
import shutil
import yaml
import os
import platform

from shutil import ignore_patterns

# -------------------------------------------------------------------------------
def copy_files(src_dir, dst_dir, ignore_list, config):
    for filename in config['files']:
        src = os.path.join(src_dir, filename)
        dst = os.path.join(dst_dir, filename)
        print("## cp '{}' => '{}'".format(filename, dst))

        if os.path.isdir(src):
            # if the folder already exists, copytree will unfortunately fail. This is fixed in 3.8+, but for now this is the easiest solution
            if os.path.exists(dst):
                shutil.rmtree(dst)
            try:
                shutil.copytree(src, dst, ignore=ignore_patterns(*ignore_list))
            except IOError as err:
                # show a proper error if file copying fails
                util.fmtError("Failed to copy folder '{}' with '{}'".format(err.filename, err.strerror))
        else:
            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            try:
                shutil.copyfile(src, dst)
            except IOError as err:
                # show a proper error if file copying fails
                util.fmtError("Failed to copy file '{}' with '{}'".format( err.filename, err.strerror))


#-------------------------------------------------------------------------------
def gen_header(out_dummy_file):
    with open(out_dummy_file, 'w') as f:
        f.write('#pragma once\n')
        f.write('//------------------------------------------------------------------------------\n')
        f.write('// #version:{}#\n'.format(Version))
        f.write('// machine generated, do not edit!\n')
        f.write('//------------------------------------------------------------------------------\n')
        f.write('// JUST A DUMMY FILE, NOTHING TO SEE HERE\n')


#-------------------------------------------------------------------------------
def check_dirty(src_root_path, input, out_dummy_file, config):
    out_files = [out_dummy_file]
    in_files = [input]
    if 'files' in config:
        for filename in config['files']:
            abs_path = os.path.abspath(os.path.join(src_root_path, filename))
            if os.path.isdir(abs_path):
                for root, dirs, files in os.walk(abs_path):
                    for file in files:
                        in_files.append(os.path.abspath(os.path.join(src_root_path, filename, file)))
            else:
                in_files.append(abs_path)

    return util.isDirty(Version, in_files, out_files)


#-------------------------------------------------------------------------------
def generate(input, out_src, out_hdr, args):
    with open(input, 'r') as f:
        try:
            config = yaml.load(f)
        except yaml.YAMLError as exc:
            # show a proper error if YAML parsing fails
            util.setErrorLocation(exc.problem_mark.name, exc.problem_mark.line-1)
            util.fmtError('YAML error: {}'.format(exc.problem))
    util.setErrorLocation(input, 1)

    src_root_path = os.path.dirname(input)
    dst_dir = args['deploy_dir']

    if 'options' in config:
        if 'src_dir' in config['options']:
            src_root_path = os.path.join(src_root_path, config['options']['src_dir'])

        if util.getEnv('target_platform') == 'ios' and 'ios' in config['options'] and 'dst_dir' in config['options']['ios']:
                dst_dir = os.path.join(dst_dir, config['options']['ios']['dst_dir'])

        elif util.getEnv('target_platform') == 'osx' and 'macos' in config['options'] and 'dst_dir' in config['options']['macos']:
                dst_dir = os.path.join(dst_dir, config['options']['macos']['dst_dir'])

        elif 'dst_dir' in config['options']:
            dst_dir = os.path.join(dst_dir, config['options']['dst_dir'])

        del config['options']

    dst_dir = dst_dir.replace('$TARGET_NAME', args['target_name'])
    out_dummy_file = os.path.join(dst_dir, os.path.basename(out_hdr))

    ignore_list = ''
    if 'ignore' in config:
        ignore_list = config['ignore']

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    if check_dirty(src_root_path, input, out_dummy_file, config):
        copy_files(src_root_path, dst_dir, ignore_list, config)
        gen_header(out_dummy_file)
