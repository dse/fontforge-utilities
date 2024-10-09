import os
import sys

stderr_fd = None

def import_fontforge():
    global stderr_fd, fontforge
    if not os.environ.get("FFUTILS_DEBUG"):
        if stderr_fd == None:
            stderr_fd = os.dup(2)
        os.close(2)
    import fontforge
    if not os.environ.get("FFUTILS_DEBUG"):
        os.dup2(stderr_fd, 2)

def load_font(filename):
    global stderr_fd, fontforge
    try:
        if not os.environ.get("FFUTILS_DEBUG"):
            os.close(2)
        font = fontforge.open(filename, ('fstypepermitted',))
        if not os.environ.get("FFUTILS_DEBUG"):
            os.dup2(stderr_fd, 2)
        return font
    except OSError as e:
        if not os.environ.get("FFUTILS_DEBUG"):
            os.dup2(stderr_fd, 2)
        sys.stderr.write("%s: %s\n" % (filename, e))
        return None

def u(codepoint):
    if codepoint < 0:
        return "%-8d" % codepoint
    return "U+%04X" % codepoint
