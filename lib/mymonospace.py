FAMILY_KIND_ANY = 0
LATIN_TEXT = 2
LATIN_HAND_WRITTEN = 3

LATIN_TEXT_MONOSPACED = 9
LATIN_HAND_WRITTEN_MONOSPACED = 3

def glyph_exclude(glyph):
    if glyph.glyphname == ".notdef" and glyph.unicode < 0 and glyph.width == 0:
        # KNOWN OK
        return True
    if glyph.glyphname == ".null" and glyph.unicode < 0 and glyph.width == 0:
        # KNOWN OK
        return True
    return False

def known_working_panose(font):
    if font.os2_panose[0] == LATIN_TEXT and font.os2_panose[3] == LATIN_TEXT_MONOSPACED:
        return True
    if font.os2_panose[0] == LATIN_HAND_WRITTEN and font.os2_panose[3] == LATIN_HAND_WRITTEN_MONOSPACED:
        return True
    if font.os2_panose[0] == FAMILY_KIND_ANY and font.os2_panose[3] == LATIN_TEXT_MONOSPACED:
        return True
    return False

def font_is_absolutely_monospace(font):
    if not known_working_panose(font):
        return False
    glyphs = [glyph for glyph in font.glyphs() if not glyph_exclude(glyph)]
    width_list = list(set([glyph.width for glyph in glyphs]))
    width_counts = {}
    for width in width_list:
        width_counts[width] = len([glyph for glyph in glyphs if glyph.width == width])
    if len(width_list) == 1:
        return True
    return False

def font_is_absolutely_not_monospace(font):
    glyphs = [glyph for glyph in font.glyphs() if not glyph_exclude(glyph)]
    width_list = list(set([glyph.width for glyph in glyphs]))
    if len(width_list) > 4:
        return True
    return False

def check_font_monospace(font):
    glyphs = [glyph for glyph in font.glyphs() if not glyph_exclude(glyph)]
    width_list = list(set([glyph.width for glyph in glyphs]))
    if len(width_list) == 1:
        return
    if len(width_list) > 4:
        return
    if not known_working_panose(font):
        print("    panose is %s" % (font.os2_panose,))
    width_counts = {}
    for width in width_list:
        width_counts[width] = len([glyph for glyph in glyphs if glyph.width == width])
    width_list.sort(key=lambda width:width_counts[width], reverse=True)
    excepted_glyphs = [glyph for glyph in glyphs if glyph.width != width_list[0]]
    for glyph in excepted_glyphs:
        print("    | %6d | %-8s | %-32s |" % (glyph.width,
                                              u(glyph.unicode),
                                              glyph.glyphname))

def u(codepoint):
    if codepoint < 0:
        return "%d" % codepoint
    return "U+%04X" % codepoint

