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

def font_is_mono(font, mostly=False, percentile=95):
    (percentage, mono_count, glyph_count, top_width) = top_glyph_width_percentage(font)
    return (percentage == 100) or (mostly and percentage >= percentile)

def top_glyph_width_percentage(font):
    width_counts = {}
    for glyph in font.glyphs():
        width = glyph.width
        if width in width_counts:
            width_counts[width] += 1
        else:
            width_counts[width] = 1
    if len(width_counts) < 1:
        return 100
    widths = list(width_counts.keys())
    widths.sort(reverse=True, key=lambda width: width_counts[width])
    return (width_counts[widths[0]] / len(list(font.glyphs())) * 100,
            width_counts[widths[0]],
            len(list(font.glyphs())),
            widths[0])

def u(codepoint):
    if codepoint < 0:
        return "%-8d" % codepoint
    return "U+%04X" % codepoint
