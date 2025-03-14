import unicodedata
import fontforge
import argparse

def Gc(codepoint):
    return unicodedata.category(chr(codepoint))

def font_has_codepoint(font, codepoint):
    name = fontforge.nameFromUnicode(codepoint)
    return name in font

def u(codepoint):
    if codepoint < 0:
        return "%d" % codepoint
    return "U+%04X" % codepoint

def run_font_coverage_cli(codepoint_list, list_name):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='+')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--missing', '-m', action='store_true')
    args = parser.parse_args()
    for filename in args.filenames:
        if len(args.filenames) > 1:
            print("%s:" % filename)
        font = fontforge.open(filename)
        wgl4_count = len(codepoint_list)
        font_count = len([codepoint for codepoint in codepoint_list if font_has_codepoint(font, codepoint)])
        print("    %d/%d (%.2f%%) printing characters in %s" % (font_count, wgl4_count, font_count / wgl4_count * 100, list_name))
        if args.verbose >= 1 or args.missing:
            missing = [codepoint for codepoint in codepoint_list if not font_has_codepoint(font, codepoint)]
            for codepoint in missing:
                print("        %-8s  %s" % (u(codepoint), unicodedata.name(chr(codepoint))))
