#-------------------------------------------------------------------------------
# fipsutil_copy()
#
#   A file copy build job to copy asset files into the project deployment directory
#
#   Also see fips-files/generators/copy.py
#
macro(fipsutil_copy yml_file)
    fips_generate(FROM ${yml_file}
        TYPE copy
        SRC_EXT ".c"
        HDR_EXT ".h"
        OUT_OF_SOURCE
        ARGS "{ deploy_dir: \"${FIPS_PROJECT_DEPLOY_DIR}\" }")
endmacro()

#-------------------------------------------------------------------------------
# fipsutil_embed()
#
#   Convert a binary file into a C array in a header, the header is generated
#   in the project directory next to the yml file.
#
#   Also see fips-files/generators/incbin.py
#
macro(fipsutil_embed yml_file hdr_name)
    fips_generate(FROM ${yml_file} TYPE embed HEADER ${hdr_name})
endmacro()
