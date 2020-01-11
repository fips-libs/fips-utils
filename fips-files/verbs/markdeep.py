import os, fnmatch, shutil, subprocess, re
from mod import log, util

def build(fips_dir, proj_dir):
    # target directory will be 'fips-deploy/[proj]-markdeep
    proj_name = util.get_project_name_from_dir(proj_dir)
    out_dir = util.get_workspace_dir(fips_dir)+'/fips-deploy/'+proj_name+'-markdeep'
    log.info('building to: {}...'.format(out_dir))
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    # check all .h files for embedded documentation
    hdrs = []
    for root, dirnames, filenames in os.walk(proj_dir):
        for filename in fnmatch.filter(filenames, '*.h'):
            hdrs.append(os.path.join(root, filename).replace('\\','/'))
    markdeep_files = []
    capture_begin = re.compile(r'/\*#\s')
    for hdr in hdrs:
        log.info('  parsing {}'.format(hdr))
        capturing = False
        markdeep_lines = []
        with open(hdr, 'r') as src:
            lines = src.readlines()
            for line in lines:
                if "#*/" in line and capturing:
                    capturing = False
                if capturing:
                    # remove trailing tab
                    if line.startswith('    '):
                        line = line[4:]
                    elif line.startswith('\t'):
                        line = line[1:]
                    markdeep_lines.append(line)
                if capture_begin.match(line) and not capturing:
                    capturing = True
        if markdeep_lines:
            markdeep_files.append(hdr)
            dst_path = out_dir + '/' + os.path.relpath(hdr,proj_dir) + '.html'
            log.info('    markdeep block(s) found, writing: {}'.format(dst_path))
            dst_dir = os.path.dirname(dst_path)
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            with open(dst_path, 'w') as dst:
                dst.write("<meta charset='utf-8' emacsmode='-*- markdown -*-'>\n")
                dst.write("<link rel='stylesheet' href='https://casual-effects.com/markdeep/latest/apidoc.css?'>\n")
                for line in markdeep_lines:
                    dst.write(line)
                dst.write("<script>markdeepOptions={tocStyle:'medium'};</script>")
                dst.write("<!-- Markdeep: --><script src='https://casual-effects.com/markdeep/latest/markdeep.min.js?'></script>")
    
    # write a toplevel index.html
    if markdeep_files:
        markdeep_files = sorted(markdeep_files)
        dst_path = out_dir + '/index.html'
        log.info('writing toc file: {}'.format(dst_path))
        with open(dst_path, 'w') as dst:
            dst.write("<meta charset='utf-8' emacsmode='-*- markdown -*-'>\n")
            dst.write("<link rel='stylesheet' href='https://casual-effects.com/markdeep/latest/apidoc.css?'>\n")
            dst.write('# {}\n'.format(proj_name))
            for hdr in markdeep_files:
                rel_path = os.path.relpath(hdr,proj_dir)
                dst.write('- [{}]({})\n'.format(rel_path, rel_path+'.html'))
            dst.write("<script>markdeepOptions={tocStyle:'medium'};</script>")
            dst.write("<!-- Markdeep: --><script src='https://casual-effects.com/markdeep/latest/markdeep.min.js?'></script>")
    else:
        log.error("no headers with embedded markdeep found in '{}'!".format(proj_dir))

# view generated markdeep in browser, we don't need a local http server for that
def view(fips_dir, proj_dir):
    proj_name = util.get_project_name_from_dir(proj_dir)
    out_dir = util.get_workspace_dir(fips_dir)+'/fips-deploy/'+proj_name+'-markdeep'
    if os.path.isfile(out_dir+'/index.html'):
        p = util.get_host_platform()
        if p == 'osx':
            subprocess.call('open index.html', cwd=out_dir, shell=True)
        elif p == 'win':
            subprocess.call('start index.html', cwd=out_dir, shell=True)
        elif p == 'linux':
            subprocess.call('xdg-open index.html', cwd=out_dir, shell=True)
    else:
        log.error('no generated index.html found: {}'.format(out_dir+'/index.html'))

# the verb's standard "run" function
def run(fips_dir, proj_dir, args):
    if len(args) > 0:
        if len(args) > 1:
            proj_name = args[1]
            proj_dir = util.get_project_dir(fips_dir, proj_name)
        if not util.is_valid_project_dir(proj_dir):
            log.error('{} is not a valid fips project!'.format(proj_name))
        if args[0] == 'build':
            build(fips_dir, proj_dir)
        elif args[0] == 'view':
            # view also build the markdown docs first
            build(fips_dir, proj_dir)
            view(fips_dir, proj_dir)
        else:
            log.error("expected 'build' or 'view' arg")
    else:
        log.error("expected 'build' or 'view' arg")

# the verb's standard "help" function
def help():
    log.info(log.YELLOW +
        "fips markdeep build [proj]\n"
        "fips markdeep view [proj]\n"+log.DEF+
        "    Generate or view Markdeep documentation webpage.\n"
        "    Parses all *.h files in a project, searches for special\n"
        "    /*# #*/ comment blocks, and extracts them into Markdeep\n"
        "    HTML files.")
