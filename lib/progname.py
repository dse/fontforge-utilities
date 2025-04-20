import os, sys
def progname_no_ext():
    return os.path.splitext(os.path.basename(sys.argv[0]))[0]
def progname():
    return os.path.basename(sys.argv[0])
