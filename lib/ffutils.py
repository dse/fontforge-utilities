# https://fontforge.org/docs/scripting/python/fontforge.html

import fontforge
import os
import re
import string
import argparse
import json
import psMat
import unicodedata
import math
import sys

class FontForgeScript:
    #
    # INVOCATION:
    #
    #     ffs = FontForgeScript(<font>)
    #
    #     parser = argparse.ArgumentParser(...)
    #     parser.add_argument('source_filename')
    #     parser.add_argument('dest_filename')
    #     args = parser.parse_args()
    #     ffs = FontForgeScript(args)
    #
    def __init__(self, arg):
        self.sourceFilename = None
        self.destFilename = None
        self.argparse = None
        self.font = None
        if arg != None:
            if isinstance(arg, argparse.Namespace):
                self.setFromArgparse(arg)
            elif isinstance(arg, fontforge.font):
                self.font = arg
    def setFromArgparse(self, args):
        self.args           = args
        self.sourceFilename = args.source_filename
        self.destFilename   = args.dest_filename
    def loadFont(self, filename = None):
        if filename == None:
            self.font = fontforge.font()
        else:
            self.font = fontforge.open(filename)
    def saveFont(self, filename = None):
        if filename == None:
            filename = self.sourceFilename
        if re.search(r'\.sfd$', filename):
            self.font.save(filename)
        else:
            flags = ('opentype',)
            self.font.generate(filename, flags = flags)

def isInvokedFromFontForge():
    return fontforge.activeFont() != None

def copyLayer(glyph, src, dest, replace = True):
    glyph.activeLayer = dest
    pen = glyph.glyphPen(replace = replace)
    glyph.activeLayer = src
    glyph.draw(pen)
    pen = None

def searchUpForFile(filename, directory = None):
    if directory == None:
        filename = os.path.abspath(filename)
    elif not os.path.isabs(filename):
        filename = os.path.abspath(os.path.join(directory, filename))
    if os.path.exists(filename):
        return filename
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    parentdirname = os.path.normpath(os.path.join(dirname, '..'))
    if dirname == parentdirname:
        return None
    return searchUpForFile(os.path.basename(filename), parentdirname)

def getFontData(pathname = None):
    if pathname == None:
        dirname = '.'
    elif os.path.isdir(pathname):
        dirname = pathname
    else:
        dirname = os.path.dirname(pathname)
    filename = searchUpForFile('.font.json', dirname)
    if filename == None:
        return None
    return json.load(open(filename))

def coalesce(*args):
    for arg in args:
        if arg != None:
            return arg
    return None

def getCoalesce(dict, key, default = None):
    if dict and key in dict:
        return dict[key]
    if default == Exception:
        raise Exception("%s not defined in .font.json" % key)
    return default

def isBoxDrawingCharacter(glyph):
    return glyph.unicode >= 0x2500 and glyph.unicode < 0x2580

def isBlockDrawingCharacter(glyph):
    return glyph.unicode >= 0x2580 and glyph.unicode < 0x25a0

def isDiagonalBoxDrawingCharacter(glyph):
    return glyph.unicode >= 0x2571 and glyph.unicode <= 0x2573

def clipGlyph(glyph, width = None):
    if width == None:
        width = glyph.width
    font = glyph.font
    clipContour = fontforge.contour()
    clipContour.moveTo(0, font.ascent)
    clipContour.lineTo(width, font.ascent)
    clipContour.lineTo(width, -font.descent)
    clipContour.lineTo(0, -font.descent)
    clipContour.closed = True
    glyph.layers['Fore'] += clipContour
    glyph.intersect()

def generateBraille(font, codepoint):
    glyphWidth = 1024
    glyphHeight = font.ascent + font.descent
    brailleScale = 0.75
    dotWidth = 112

    try:
        char = unichr(codepoint)
    except NameError:
        char = chr(codepoint)
    try:
        charName = unicodedata.name(char)
    except ValueError:
        raise Exception("invalid codepoint: U+%04X (%d)" % (codepoint, codepoint))

    matchBlank = re.search(' BLANK$', charName)
    matchDots = re.search('-([0-9]+)$', charName)
    if (not matchBlank) and (not matchDots):
        raise Exception("invalid braille glyph name: U+%04X %s (%d)" % (codepoint, charName, codepoint))
    if matchDots:
        dotString = matchDots.group(1)

    glyph = None
    if codepoint in font:
        glyph = font[codepoint]
        glyph.clear()
    else:
        glyph = font.createChar(codepoint)

    if matchDots:
        # where dots 1 through 8 are located
        dotsXX = [0, 0, 0, 1, 1, 1, 0, 1]
        dotsYY = [0, 1, 2, 0, 1, 2, 3, 3]

        middleX = int(0.5 + float(glyphWidth) / 2.0)
        middleY = int(0.5 + (float(font.ascent) - float(abs(font.descent))) / 2)

        glyph.activeLayer = 'Fore'
        pen = glyph.glyphPen()
        for dotNumberChar in dotString:
            dotNumber = int(dotNumberChar) - 1
            dotXX = dotsXX[dotNumber]
            dotYY = dotsYY[dotNumber]
            dotX = int(0.5 + (
                float(middleX) + (float(dotXX) - 0.5) * float(glyphWidth) / 2 * brailleScale
            ))
            dotY = int(0.5 + (
                float(middleY) - (float(dotYY) - 1.5) * float(glyphHeight) / 4 * brailleScale
            ))
            circle = fontforge.unitShape(0)
            circle.transform(psMat.scale(dotWidth))
            circle.transform(psMat.translate(dotX, dotY))
            circle.draw(pen)
        pen = None

    glyph.width = glyphWidth

# originally for use with DSE Typewriter
def updateBackgroundStrokeGlyph(glyph):
    font = glyph.font
    bg = glyph.background
    fg = glyph.foreground
    clip = False

    if not bg.isEmpty():
        savedWidth = glyph.width

        # make heavy box drawing character segments heavier
        middleX = int(0.5 + 1.0 * glyph.width / 2)
        middleY = int(0.5 + 1.0 * (font.ascent - abs(font.descent)) / 2)
        backLayer = glyph.layers['Back']

        # legacy
        if (glyph.unicode >= 0x2500 and glyph.unicode <= 0x254f) or (glyph.unicode >= 0x2574 and glyph.unicode <= 0x257f):
            modifyBackLayer = False
            contours = []
            newContours = []
            for contour in backLayer:
                contours += [contour]
                newContour = fontforge.contour()
                for point in contour:
                    if point.x == middleX - 48:
                        modifyBackLayer = True
                        point.x = middleX - 96
                    if point.x == middleX + 48:
                        modifyBackLayer = True
                        point.x = middleX + 96
                    if point.y == middleY - 48:
                        modifyBackLayer = True
                        point.y = middleY - 96
                    if point.y == middleY + 48:
                        modifyBackLayer = True
                        point.y = middleY + 96
                    newContour += point
                newContours += [newContour]
            if modifyBackLayer:
                glyph.layers['Back'] = fontforge.layer()
                for contour in newContours:
                    glyph.layers['Back'] += contour
                backLayer = glyph.layers['Back']

        # save anchor points
        glyph.activeLayer = 'Fore'
        anchorPoints = glyph.anchorPoints

        # save foreground references, for glyphs combining
        # foreground-layer references and background-layer strokes
        references = glyph.layerrefs[1]

        copyLayer(glyph, src = 'Back', dest = 'Fore')

        strokeWidth = 96

        if (isBoxDrawingCharacter(glyph) and not
            isDiagonalBoxDrawingCharacter(glyph)):
            # Box Drawing Characters
            lineCap = 'butt'
            lineJoin = 'round'
        else:
            lineCap = 'round'
            lineJoin = 'round'

        glyph.activeLayer = 'Fore'
        if font.fontname == 'DSETypewriter' and glyph.unicode in [0x3b1, 0x3b4]:
            print('wheeee')
            glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
        else:
            glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
            glyph.removeOverlap()
        glyph.width = savedWidth

        # originally for U+2571 through U+2573 but would not work
        if clip:
            clipGlyph(glyph)

        glyph.addExtrema()

        # restore anchor points
        glyph.activeLayer = 'Fore'
        for anchorPoint in anchorPoints:
            glyph.addAnchorPoint(*anchorPoint)

        for reference in references:
            glyph.addReference(reference[0], reference[1])

# https://stackoverflow.com/questions/243831/unicode-block-of-a-character-in-python
class UnicodeBlocks:
    @classmethod
    def block(cls, char):
        if type(char) == int:
            return cls.blockFromCodepoint(char)
        elif type(char) == float:
            return cls.blockFromCodepoint(int(char))
        elif str != bytes:      # python >= 3
            if type(char) == bytes:
                return cls.blockFromCodepoint(ord(char))
            elif type(char) == str:
                return cls.blockFromCodepoint(ord(char))
        else:
            if type(char) == unicode:
                return cls.blockFromCodepoint(ord(char))
            elif type(char) == str:
                return cls.blockFromCodepoint(ord(char))

    @classmethod
    def blockFromCodepoint(cls, codepoint):
        for start, end, name in cls.blocks:
            if start <= codepoint <= end:
                return name
    @classmethod
    def initBlocks(cls, text):
        cls.blocks = []
        import re
        pattern = re.compile(r'([0-9A-F]+)\.\.([0-9A-F]+);\ (\S.*\S)')
        for line in re.split(r'\r\n?|\n', text):
            m = pattern.match(line)
            if m:
                start, end, name = m.groups()
                cls.blocks.append((int(start, 16), int(end, 16), name))

    @classmethod
    def blockNames(cls):
        return [block[2] for block in cls.blocks]

    @classmethod
    def blockRange(cls, blockName):
        for block in cls.blocks:
            if blockName == block[2]:
                return range(block[0], block[1] + 1)

    try:
        unicode = unicode
    except NameError:
        unicode = str

UnicodeBlocks.WGL4 = [0x0020, 0x0021, 0x0022, 0x0023, 0x0024, 0x0025,
                      0x0026, 0x0027, 0x0028, 0x0029, 0x002a, 0x002b,
                      0x002c, 0x002d, 0x002e, 0x002f, 0x0030, 0x0031,
                      0x0032, 0x0033, 0x0034, 0x0035, 0x0036, 0x0037,
                      0x0038, 0x0039, 0x003a, 0x003b, 0x003c, 0x003d,
                      0x003e, 0x003f, 0x0040, 0x0041, 0x0042, 0x0043,
                      0x0044, 0x0045, 0x0046, 0x0047, 0x0048, 0x0049,
                      0x004a, 0x004b, 0x004c, 0x004d, 0x004e, 0x004f,
                      0x0050, 0x0051, 0x0052, 0x0053, 0x0054, 0x0055,
                      0x0056, 0x0057, 0x0058, 0x0059, 0x005a, 0x005b,
                      0x005c, 0x005d, 0x005e, 0x005f, 0x0060, 0x0061,
                      0x0062, 0x0063, 0x0064, 0x0065, 0x0066, 0x0067,
                      0x0068, 0x0069, 0x006a, 0x006b, 0x006c, 0x006d,
                      0x006e, 0x006f, 0x0070, 0x0071, 0x0072, 0x0073,
                      0x0074, 0x0075, 0x0076, 0x0077, 0x0078, 0x0079,
                      0x007a, 0x007b, 0x007c, 0x007d, 0x007e, 0x00a0,
                      0x00a1, 0x00a2, 0x00a3, 0x00a4, 0x00a5, 0x00a6,
                      0x00a7, 0x00a8, 0x00a9, 0x00aa, 0x00ab, 0x00ac,
                      0x00ad, 0x00ae, 0x00af, 0x00b0, 0x00b1, 0x00b2,
                      0x00b3, 0x00b4, 0x00b5, 0x00b6, 0x00b7, 0x00b8,
                      0x00b9, 0x00ba, 0x00bb, 0x00bc, 0x00bd, 0x00be,
                      0x00bf, 0x00c0, 0x00c1, 0x00c2, 0x00c3, 0x00c4,
                      0x00c5, 0x00c6, 0x00c7, 0x00c8, 0x00c9, 0x00ca,
                      0x00cb, 0x00cc, 0x00cd, 0x00ce, 0x00cf, 0x00d0,
                      0x00d1, 0x00d2, 0x00d3, 0x00d4, 0x00d5, 0x00d6,
                      0x00d7, 0x00d8, 0x00d9, 0x00da, 0x00db, 0x00dc,
                      0x00dd, 0x00de, 0x00df, 0x00e0, 0x00e1, 0x00e2,
                      0x00e3, 0x00e4, 0x00e5, 0x00e6, 0x00e7, 0x00e8,
                      0x00e9, 0x00ea, 0x00eb, 0x00ec, 0x00ed, 0x00ee,
                      0x00ef, 0x00f0, 0x00f1, 0x00f2, 0x00f3, 0x00f4,
                      0x00f5, 0x00f6, 0x00f7, 0x00f8, 0x00f9, 0x00fa,
                      0x00fb, 0x00fc, 0x00fd, 0x00fe, 0x00ff, 0x0100,
                      0x0101, 0x0102, 0x0103, 0x0104, 0x0105, 0x0106,
                      0x0107, 0x0108, 0x0109, 0x010a, 0x010b, 0x010c,
                      0x010d, 0x010e, 0x010f, 0x0110, 0x0111, 0x0112,
                      0x0113, 0x0114, 0x0115, 0x0116, 0x0117, 0x0118,
                      0x0119, 0x011a, 0x011b, 0x011c, 0x011d, 0x011e,
                      0x011f, 0x0120, 0x0121, 0x0122, 0x0123, 0x0124,
                      0x0125, 0x0126, 0x0127, 0x0128, 0x0129, 0x012a,
                      0x012b, 0x012c, 0x012d, 0x012e, 0x012f, 0x0130,
                      0x0131, 0x0132, 0x0133, 0x0134, 0x0135, 0x0136,
                      0x0137, 0x0138, 0x0139, 0x013a, 0x013b, 0x013c,
                      0x013d, 0x013e, 0x013f, 0x0140, 0x0141, 0x0142,
                      0x0143, 0x0144, 0x0145, 0x0146, 0x0147, 0x0148,
                      0x0149, 0x014a, 0x014b, 0x014c, 0x014d, 0x014e,
                      0x014f, 0x0150, 0x0151, 0x0152, 0x0153, 0x0154,
                      0x0155, 0x0156, 0x0157, 0x0158, 0x0159, 0x015a,
                      0x015b, 0x015c, 0x015d, 0x015e, 0x015f, 0x0160,
                      0x0161, 0x0162, 0x0163, 0x0164, 0x0165, 0x0166,
                      0x0167, 0x0168, 0x0169, 0x016a, 0x016b, 0x016c,
                      0x016d, 0x016e, 0x016f, 0x0170, 0x0171, 0x0172,
                      0x0173, 0x0174, 0x0175, 0x0176, 0x0177, 0x0178,
                      0x0179, 0x017a, 0x017b, 0x017c, 0x017d, 0x017e,
                      0x017f, 0x0192, 0x01fa, 0x01fb, 0x01fc, 0x01fd,
                      0x01fe, 0x01ff, 0x02c6, 0x02c7, 0x02c9, 0x02d8,
                      0x02d9, 0x02da, 0x02db, 0x02dc, 0x02dd, 0x0384,
                      0x0385, 0x0386, 0x0387, 0x0388, 0x0389, 0x038a,
                      0x038c, 0x038e, 0x038f, 0x0390, 0x0391, 0x0392,
                      0x0393, 0x0394, 0x0395, 0x0396, 0x0397, 0x0398,
                      0x0399, 0x039a, 0x039b, 0x039c, 0x039d, 0x039e,
                      0x039f, 0x03a0, 0x03a1, 0x03a3, 0x03a4, 0x03a5,
                      0x03a6, 0x03a7, 0x03a8, 0x03a9, 0x03aa, 0x03ab,
                      0x03ac, 0x03ad, 0x03ae, 0x03af, 0x03b0, 0x03b1,
                      0x03b2, 0x03b3, 0x03b4, 0x03b5, 0x03b6, 0x03b7,
                      0x03b8, 0x03b9, 0x03ba, 0x03bb, 0x03bc, 0x03bd,
                      0x03be, 0x03bf, 0x03c0, 0x03c1, 0x03c2, 0x03c3,
                      0x03c4, 0x03c5, 0x03c6, 0x03c7, 0x03c8, 0x03c9,
                      0x03ca, 0x03cb, 0x03cc, 0x03cd, 0x03ce, 0x0400,
                      0x0401, 0x0402, 0x0403, 0x0404, 0x0405, 0x0406,
                      0x0407, 0x0408, 0x0409, 0x040a, 0x040b, 0x040c,
                      0x040D, 0x040e, 0x040f, 0x0410, 0x0411, 0x0412,
                      0x0413, 0x0414, 0x0415, 0x0416, 0x0417, 0x0418,
                      0x0419, 0x041a, 0x041b, 0x041c, 0x041d, 0x041e,
                      0x041f, 0x0420, 0x0421, 0x0422, 0x0423, 0x0424,
                      0x0425, 0x0426, 0x0427, 0x0428, 0x0429, 0x042a,
                      0x042b, 0x042c, 0x042d, 0x042e, 0x042f, 0x0430,
                      0x0431, 0x0432, 0x0433, 0x0434, 0x0435, 0x0436,
                      0x0437, 0x0438, 0x0439, 0x043a, 0x043b, 0x043c,
                      0x043d, 0x043e, 0x043f, 0x0440, 0x0441, 0x0442,
                      0x0443, 0x0444, 0x0445, 0x0446, 0x0447, 0x0448,
                      0x0449, 0x044a, 0x044b, 0x044c, 0x044d, 0x044e,
                      0x044f, 0x0450, 0x0451, 0x0452, 0x0453, 0x0454,
                      0x0455, 0x0456, 0x0457, 0x0458, 0x0459, 0x045a,
                      0x045b, 0x045c, 0x045D, 0x045e, 0x045f, 0x0490,
                      0x0491, 0x1e80, 0x1e81, 0x1e82, 0x1e83, 0x1e84,
                      0x1e85, 0x1ef2, 0x1ef3, 0x2013, 0x2014, 0x2015,
                      0x2017, 0x2018, 0x2019, 0x201a, 0x201b, 0x201c,
                      0x201d, 0x201e, 0x2020, 0x2021, 0x2022, 0x2026,
                      0x2030, 0x2032, 0x2033, 0x2039, 0x203a, 0x203c,
                      0x203e, 0x2044, 0x207f, 0x20a3, 0x20a4, 0x20a7,
                      0x20ac, 0x2105, 0x2113, 0x2116, 0x2122, 0x2126,
                      0x212e, 0x215b, 0x215c, 0x215d, 0x215e, 0x2190,
                      0x2191, 0x2192, 0x2193, 0x2194, 0x2195, 0x21a8,
                      0x2202, 0x2206, 0x220f, 0x2211, 0x2212, 0x2215,
                      0x2219, 0x221a, 0x221e, 0x221f, 0x2229, 0x222b,
                      0x2248, 0x2260, 0x2261, 0x2264, 0x2265, 0x2302,
                      0x2310, 0x2320, 0x2321, 0x2500, 0x2502, 0x250c,
                      0x2510, 0x2514, 0x2518, 0x251c, 0x2524, 0x252c,
                      0x2534, 0x253c, 0x2550, 0x2551, 0x2552, 0x2553,
                      0x2554, 0x2555, 0x2556, 0x2557, 0x2558, 0x2559,
                      0x255a, 0x255b, 0x255c, 0x255d, 0x255e, 0x255f,
                      0x2560, 0x2561, 0x2562, 0x2563, 0x2564, 0x2565,
                      0x2566, 0x2567, 0x2568, 0x2569, 0x256a, 0x256b,
                      0x256c, 0x2580, 0x2584, 0x2588, 0x258c, 0x2590,
                      0x2591, 0x2592, 0x2593, 0x25a0, 0x25a1, 0x25aa,
                      0x25ab, 0x25ac, 0x25b2, 0x25ba, 0x25bc, 0x25c4,
                      0x25ca, 0x25cb, 0x25cf, 0x25d8, 0x25d9, 0x25e6,
                      0x263a, 0x263b, 0x263c, 0x2640, 0x2642, 0x2660,
                      0x2663, 0x2665, 0x2666, 0x266a, 0x266b, 0xf001,
                      0xf002, 0xfb01, 0xfb02]
# http://www.unicode.org/Public/UNIDATA/Blocks.txt
UnicodeBlocks.initBlocks('''
# Blocks-13.0.0.txt
# Date: 2019-07-10, 19:06:00 GMT [KW]
# © 2019 Unicode®, Inc.
# For terms of use, see http://www.unicode.org/terms_of_use.html
#
# Unicode Character Database
# For documentation, see http://www.unicode.org/reports/tr44/
#
# Format:
# Start Code..End Code; Block Name

# ================================================

# Note:   When comparing block names, casing, whitespace, hyphens,
#         and underbars are ignored.
#         For example, "Latin Extended-A" and "latin extended a" are equivalent.
#         For more information on the comparison of property values,
#            see UAX #44: http://www.unicode.org/reports/tr44/
#
#  All block ranges start with a value where (cp MOD 16) = 0,
#  and end with a value where (cp MOD 16) = 15. In other words,
#  the last hexadecimal digit of the start of range is ...0
#  and the last hexadecimal digit of the end of range is ...F.
#  This constraint on block ranges guarantees that allocations
#  are done in terms of whole columns, and that code chart display
#  never involves splitting columns in the charts.
#
#  All code points not explicitly listed for Block
#  have the value No_Block.

# Property:	Block
#
# @missing: 0000..10FFFF; No_Block

0000..007F; Basic Latin
0080..00FF; Latin-1 Supplement
0100..017F; Latin Extended-A
0180..024F; Latin Extended-B
0250..02AF; IPA Extensions
02B0..02FF; Spacing Modifier Letters
0300..036F; Combining Diacritical Marks
0370..03FF; Greek and Coptic
0400..04FF; Cyrillic
0500..052F; Cyrillic Supplement
0530..058F; Armenian
0590..05FF; Hebrew
0600..06FF; Arabic
0700..074F; Syriac
0750..077F; Arabic Supplement
0780..07BF; Thaana
07C0..07FF; NKo
0800..083F; Samaritan
0840..085F; Mandaic
0860..086F; Syriac Supplement
08A0..08FF; Arabic Extended-A
0900..097F; Devanagari
0980..09FF; Bengali
0A00..0A7F; Gurmukhi
0A80..0AFF; Gujarati
0B00..0B7F; Oriya
0B80..0BFF; Tamil
0C00..0C7F; Telugu
0C80..0CFF; Kannada
0D00..0D7F; Malayalam
0D80..0DFF; Sinhala
0E00..0E7F; Thai
0E80..0EFF; Lao
0F00..0FFF; Tibetan
1000..109F; Myanmar
10A0..10FF; Georgian
1100..11FF; Hangul Jamo
1200..137F; Ethiopic
1380..139F; Ethiopic Supplement
13A0..13FF; Cherokee
1400..167F; Unified Canadian Aboriginal Syllabics
1680..169F; Ogham
16A0..16FF; Runic
1700..171F; Tagalog
1720..173F; Hanunoo
1740..175F; Buhid
1760..177F; Tagbanwa
1780..17FF; Khmer
1800..18AF; Mongolian
18B0..18FF; Unified Canadian Aboriginal Syllabics Extended
1900..194F; Limbu
1950..197F; Tai Le
1980..19DF; New Tai Lue
19E0..19FF; Khmer Symbols
1A00..1A1F; Buginese
1A20..1AAF; Tai Tham
1AB0..1AFF; Combining Diacritical Marks Extended
1B00..1B7F; Balinese
1B80..1BBF; Sundanese
1BC0..1BFF; Batak
1C00..1C4F; Lepcha
1C50..1C7F; Ol Chiki
1C80..1C8F; Cyrillic Extended-C
1C90..1CBF; Georgian Extended
1CC0..1CCF; Sundanese Supplement
1CD0..1CFF; Vedic Extensions
1D00..1D7F; Phonetic Extensions
1D80..1DBF; Phonetic Extensions Supplement
1DC0..1DFF; Combining Diacritical Marks Supplement
1E00..1EFF; Latin Extended Additional
1F00..1FFF; Greek Extended
2000..206F; General Punctuation
2070..209F; Superscripts and Subscripts
20A0..20CF; Currency Symbols
20D0..20FF; Combining Diacritical Marks for Symbols
2100..214F; Letterlike Symbols
2150..218F; Number Forms
2190..21FF; Arrows
2200..22FF; Mathematical Operators
2300..23FF; Miscellaneous Technical
2400..243F; Control Pictures
2440..245F; Optical Character Recognition
2460..24FF; Enclosed Alphanumerics
2500..257F; Box Drawing
2580..259F; Block Elements
25A0..25FF; Geometric Shapes
2600..26FF; Miscellaneous Symbols
2700..27BF; Dingbats
27C0..27EF; Miscellaneous Mathematical Symbols-A
27F0..27FF; Supplemental Arrows-A
2800..28FF; Braille Patterns
2900..297F; Supplemental Arrows-B
2980..29FF; Miscellaneous Mathematical Symbols-B
2A00..2AFF; Supplemental Mathematical Operators
2B00..2BFF; Miscellaneous Symbols and Arrows
2C00..2C5F; Glagolitic
2C60..2C7F; Latin Extended-C
2C80..2CFF; Coptic
2D00..2D2F; Georgian Supplement
2D30..2D7F; Tifinagh
2D80..2DDF; Ethiopic Extended
2DE0..2DFF; Cyrillic Extended-A
2E00..2E7F; Supplemental Punctuation
2E80..2EFF; CJK Radicals Supplement
2F00..2FDF; Kangxi Radicals
2FF0..2FFF; Ideographic Description Characters
3000..303F; CJK Symbols and Punctuation
3040..309F; Hiragana
30A0..30FF; Katakana
3100..312F; Bopomofo
3130..318F; Hangul Compatibility Jamo
3190..319F; Kanbun
31A0..31BF; Bopomofo Extended
31C0..31EF; CJK Strokes
31F0..31FF; Katakana Phonetic Extensions
3200..32FF; Enclosed CJK Letters and Months
3300..33FF; CJK Compatibility
3400..4DBF; CJK Unified Ideographs Extension A
4DC0..4DFF; Yijing Hexagram Symbols
4E00..9FFF; CJK Unified Ideographs
A000..A48F; Yi Syllables
A490..A4CF; Yi Radicals
A4D0..A4FF; Lisu
A500..A63F; Vai
A640..A69F; Cyrillic Extended-B
A6A0..A6FF; Bamum
A700..A71F; Modifier Tone Letters
A720..A7FF; Latin Extended-D
A800..A82F; Syloti Nagri
A830..A83F; Common Indic Number Forms
A840..A87F; Phags-pa
A880..A8DF; Saurashtra
A8E0..A8FF; Devanagari Extended
A900..A92F; Kayah Li
A930..A95F; Rejang
A960..A97F; Hangul Jamo Extended-A
A980..A9DF; Javanese
A9E0..A9FF; Myanmar Extended-B
AA00..AA5F; Cham
AA60..AA7F; Myanmar Extended-A
AA80..AADF; Tai Viet
AAE0..AAFF; Meetei Mayek Extensions
AB00..AB2F; Ethiopic Extended-A
AB30..AB6F; Latin Extended-E
AB70..ABBF; Cherokee Supplement
ABC0..ABFF; Meetei Mayek
AC00..D7AF; Hangul Syllables
D7B0..D7FF; Hangul Jamo Extended-B
D800..DB7F; High Surrogates
DB80..DBFF; High Private Use Surrogates
DC00..DFFF; Low Surrogates
E000..F8FF; Private Use Area
F900..FAFF; CJK Compatibility Ideographs
FB00..FB4F; Alphabetic Presentation Forms
FB50..FDFF; Arabic Presentation Forms-A
FE00..FE0F; Variation Selectors
FE10..FE1F; Vertical Forms
FE20..FE2F; Combining Half Marks
FE30..FE4F; CJK Compatibility Forms
FE50..FE6F; Small Form Variants
FE70..FEFF; Arabic Presentation Forms-B
FF00..FFEF; Halfwidth and Fullwidth Forms
FFF0..FFFF; Specials
10000..1007F; Linear B Syllabary
10080..100FF; Linear B Ideograms
10100..1013F; Aegean Numbers
10140..1018F; Ancient Greek Numbers
10190..101CF; Ancient Symbols
101D0..101FF; Phaistos Disc
10280..1029F; Lycian
102A0..102DF; Carian
102E0..102FF; Coptic Epact Numbers
10300..1032F; Old Italic
10330..1034F; Gothic
10350..1037F; Old Permic
10380..1039F; Ugaritic
103A0..103DF; Old Persian
10400..1044F; Deseret
10450..1047F; Shavian
10480..104AF; Osmanya
104B0..104FF; Osage
10500..1052F; Elbasan
10530..1056F; Caucasian Albanian
10600..1077F; Linear A
10800..1083F; Cypriot Syllabary
10840..1085F; Imperial Aramaic
10860..1087F; Palmyrene
10880..108AF; Nabataean
108E0..108FF; Hatran
10900..1091F; Phoenician
10920..1093F; Lydian
10980..1099F; Meroitic Hieroglyphs
109A0..109FF; Meroitic Cursive
10A00..10A5F; Kharoshthi
10A60..10A7F; Old South Arabian
10A80..10A9F; Old North Arabian
10AC0..10AFF; Manichaean
10B00..10B3F; Avestan
10B40..10B5F; Inscriptional Parthian
10B60..10B7F; Inscriptional Pahlavi
10B80..10BAF; Psalter Pahlavi
10C00..10C4F; Old Turkic
10C80..10CFF; Old Hungarian
10D00..10D3F; Hanifi Rohingya
10E60..10E7F; Rumi Numeral Symbols
10E80..10EBF; Yezidi
10F00..10F2F; Old Sogdian
10F30..10F6F; Sogdian
10FB0..10FDF; Chorasmian
10FE0..10FFF; Elymaic
11000..1107F; Brahmi
11080..110CF; Kaithi
110D0..110FF; Sora Sompeng
11100..1114F; Chakma
11150..1117F; Mahajani
11180..111DF; Sharada
111E0..111FF; Sinhala Archaic Numbers
11200..1124F; Khojki
11280..112AF; Multani
112B0..112FF; Khudawadi
11300..1137F; Grantha
11400..1147F; Newa
11480..114DF; Tirhuta
11580..115FF; Siddham
11600..1165F; Modi
11660..1167F; Mongolian Supplement
11680..116CF; Takri
11700..1173F; Ahom
11800..1184F; Dogra
118A0..118FF; Warang Citi
11900..1195F; Dives Akuru
119A0..119FF; Nandinagari
11A00..11A4F; Zanabazar Square
11A50..11AAF; Soyombo
11AC0..11AFF; Pau Cin Hau
11C00..11C6F; Bhaiksuki
11C70..11CBF; Marchen
11D00..11D5F; Masaram Gondi
11D60..11DAF; Gunjala Gondi
11EE0..11EFF; Makasar
11FB0..11FBF; Lisu Supplement
11FC0..11FFF; Tamil Supplement
12000..123FF; Cuneiform
12400..1247F; Cuneiform Numbers and Punctuation
12480..1254F; Early Dynastic Cuneiform
13000..1342F; Egyptian Hieroglyphs
13430..1343F; Egyptian Hieroglyph Format Controls
14400..1467F; Anatolian Hieroglyphs
16800..16A3F; Bamum Supplement
16A40..16A6F; Mro
16AD0..16AFF; Bassa Vah
16B00..16B8F; Pahawh Hmong
16E40..16E9F; Medefaidrin
16F00..16F9F; Miao
16FE0..16FFF; Ideographic Symbols and Punctuation
17000..187FF; Tangut
18800..18AFF; Tangut Components
18B00..18CFF; Khitan Small Script
18D00..18D8F; Tangut Supplement
1B000..1B0FF; Kana Supplement
1B100..1B12F; Kana Extended-A
1B130..1B16F; Small Kana Extension
1B170..1B2FF; Nushu
1BC00..1BC9F; Duployan
1BCA0..1BCAF; Shorthand Format Controls
1D000..1D0FF; Byzantine Musical Symbols
1D100..1D1FF; Musical Symbols
1D200..1D24F; Ancient Greek Musical Notation
1D2E0..1D2FF; Mayan Numerals
1D300..1D35F; Tai Xuan Jing Symbols
1D360..1D37F; Counting Rod Numerals
1D400..1D7FF; Mathematical Alphanumeric Symbols
1D800..1DAAF; Sutton SignWriting
1E000..1E02F; Glagolitic Supplement
1E100..1E14F; Nyiakeng Puachue Hmong
1E2C0..1E2FF; Wancho
1E800..1E8DF; Mende Kikakui
1E900..1E95F; Adlam
1EC70..1ECBF; Indic Siyaq Numbers
1ED00..1ED4F; Ottoman Siyaq Numbers
1EE00..1EEFF; Arabic Mathematical Alphabetic Symbols
1F000..1F02F; Mahjong Tiles
1F030..1F09F; Domino Tiles
1F0A0..1F0FF; Playing Cards
1F100..1F1FF; Enclosed Alphanumeric Supplement
1F200..1F2FF; Enclosed Ideographic Supplement
1F300..1F5FF; Miscellaneous Symbols and Pictographs
1F600..1F64F; Emoticons
1F650..1F67F; Ornamental Dingbats
1F680..1F6FF; Transport and Map Symbols
1F700..1F77F; Alchemical Symbols
1F780..1F7FF; Geometric Shapes Extended
1F800..1F8FF; Supplemental Arrows-C
1F900..1F9FF; Supplemental Symbols and Pictographs
1FA00..1FA6F; Chess Symbols
1FA70..1FAFF; Symbols and Pictographs Extended-A
1FB00..1FBFF; Symbols for Legacy Computing
20000..2A6DF; CJK Unified Ideographs Extension B
2A700..2B73F; CJK Unified Ideographs Extension C
2B740..2B81F; CJK Unified Ideographs Extension D
2B820..2CEAF; CJK Unified Ideographs Extension E
2CEB0..2EBEF; CJK Unified Ideographs Extension F
2F800..2FA1F; CJK Compatibility Ideographs Supplement
30000..3134F; CJK Unified Ideographs Extension G
E0000..E007F; Tags
E0100..E01EF; Variation Selectors Supplement
F0000..FFFFF; Supplementary Private Use Area-A
100000..10FFFF; Supplementary Private Use Area-B

# EOF
''')
