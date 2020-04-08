# https://fontforge.org/docs/scripting/python/fontforge.html

import fontforge, os, re, string, argparse

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
    def getcwd(self, filename = None):
        if filename == None:
            filename = self.sourceFilename
        if filename != None:
            return os.path.dirname(os.path.realpath(filename))

def isInvokedFromFontForge():
    return fontforge.activeFont() != None

def generateBraille(font, codepoint):
    glyphHeight = font.ascent + font.descent # 2048 or 1024
    glyphWidth = glyphHeight / 2             # 1024 or 512
    brailleScale = 0.75
    dotWidth = int(glyphHeight / 16 * 0.875) # 112 or 56

    try:
        char = unichr(codepoint)
    except NameError:
        char = chr(codepoint)
    try:
        charName = unicodedata.name(char)
    except ValueError:
        sys.stderr.write("%d: not a valid codepoint." % codepoint)
        return

    matchBlank = re.search(' BLANK$', charName)
    matchDots = re.search('-([0-9]+)$', charName)
    if (not matchBlank) and (not matchDots):
        sys.stderr.write("%d: Glyph name '%s' does not look like a Unicode Braille glyph name." % (codepoint, charName))
        return
    if matchDots:
        dotString = matchDots.group(1)

    glyph = None
    if codepoint in activeFont:
        glyph = activeFont[codepoint]
        glyph.clear()
    else:
        glyph = activeFont.createChar(codepoint)

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
            print("<%d %d %d %d>" % (middleX, dotXX, glyphWidth, dotX))
            dotY = int(0.5 + (
                float(middleY) - (float(dotYY) - 1.5) * float(glyphHeight) / 4 * brailleScale
            ))
            circle = fontforge.unitShape(0)
            circle.transform(psMat.scale(dotWidth))
            circle.transform(psMat.translate(dotX, dotY))
            circle.draw(pen)
        pen = None

    glyph.width = glyphWidth

def copyLayer(glyph, src, dest, replace = True):
    glyph.activeLayer = dest
    pen = glyph.glyphPen(replace = replace)
    glyph.activeLayer = src
    glyph.draw(pen)
    pen = None

# Move contours from foreground layer to background layer.
# If background layer is not empty, do nothing.
def foreToBack(glyph):
    bg = glyph.background
    fg = glyph.foreground
    if not bg.isEmpty():
        return

    # save anchor points and references
    glyph.activeLayer = 'Fore'
    anchorPoints = glyph.anchorPoints
    references = glyph.layerrefs[1]

    # draw foreground contours to background
    glyph.activeLayer = 'Back' # dest
    pen = glyph.glyphPen(replace = True)
    glyph.activeLayer = 'Fore' # src
    glyph.draw(pen)
    pen = None

    # erase foreground layer
    glyph.activeLayer = 'Fore'
    pen = glyph.glyphPen(replace = True)
    pen = None

    # restore anchor points and references
    glyph.activeLayer = 'Fore'
    for anchorPoint in anchorPoints:
        glyph.addAnchorPoint(*anchorPoint)
    for reference in references:
        glyph.addReference(reference[0], reference[1])

def makeBoxDrawingHeavier(glyph):
    font = glyph.font
    if not (glyph.unicode >= 0x2500 and glyph.unicode <= 0x254f) or (glyph.unicode >= 0x2574 and glyph.unicode <= 0x257f):
        return

    middleX = int(0.5 + 1.0 * glyph.width / 2)
    middleY = int(0.5 + 1.0 * (font.ascent - abs(font.descent)) / 2)
    backLayer = glyph.layers['Back']

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

# Copy contours from background to foreground, and stroke them.
def strokeGlyph(glyph):
    font = glyph.font
    bg = glyph.background
    fg = glyph.foreground
    if bg.isEmpty():
        return

    savedWidth = glyph.width

    # save anchor points and references
    glyph.activeLayer = 'Fore'
    anchorPoints = glyph.anchorPoints
    references = glyph.layerrefs[1]

    copyLayer(glyph, src = 'Back', dest = 'Fore')

    strokeWidth = 96
    if font.fontname == 'RoutedGothic':
        strokeWidth = 96

    if (glyph.unicode >= 0x2500 and glyph.unicode < 0x2600 and not (glyph.unicode >= 0x2571 and glyph.unicode <= 0x2573)):
        # Box Drawing Characters
        lineCap = 'butt'
        lineJoin = 'round'
    else:
        lineCap = 'round'
        lineJoin = 'round'

    if font.fontname == 'RoutedGothic':
        print("is routed gothic")
        glyph.activeLayer = 'Fore'

        if glyph.glyphname == 'zero.ss02':
            glyph.stroke('circular', strokeWidth, lineCap, lineJoin, removeoverlap = "none")

        elif glyph.unicode in [0x21, 0x2e, 0x3a, 0x3b, 0x3f, 0xb7, 0xbf, 0xf7, 0x2022, 0x203c, 0x203d]:
            glyph.stroke('circular', strokeWidth, lineCap, lineJoin, removeoverlap = "none")

        elif glyph.unicode in [0x34, 0x26, 0x36, 0x39, 0x52, 0xe6, 0xae,
                               0x2074, 0x2076, 0x2079, 0x2084, 0x2086, 0x2089]:
            glyph.stroke('circular', strokeWidth, lineCap, lineJoin, removeoverlap = "none")
            glyph.correctDirection()

        else:
            glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
            glyph.correctDirection()

        glyph.removeOverlap()
    else:
        print("is not routed gothic")
        glyph.activeLayer = 'Fore'
        glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
        glyph.removeOverlap()

    glyph.width = savedWidth

    # restore anchor points and references
    glyph.activeLayer = 'Fore'
    for anchorPoint in anchorPoints:
        glyph.addAnchorPoint(*anchorPoint)
    for reference in references:
        glyph.addReference(reference[0], reference[1])

def clipGlyph(glyph):
    font = glyph.font
    clipContour = fontforge.contour()
    clipContour.moveTo(0, font.ascent)
    clipContour.lineTo(glyph.width, font.ascent)
    clipContour.lineTo(glyph.width, -font.descent)
    clipContour.lineTo(0, -font.descent)
    clipContour.closed = True
    glyph.layers['Fore'] += clipContour
    glyph.intersect()
    glyph.addExtrema()

# the following arguments are accepted:
#     0 to 9
#     '0' to '9'
#     48 to 57       # ord('0') to ord('9')
def subscriptCodepoint(whatever):
    if whatever in range(10):
        return ord(unicodedata.lookup('SUPERSCRIPT ' + whatever))
    if whatever in range(48, 58):
        return ord(unicodedata.lookup('SUPERSCRIPT ' + (whatever - 48)))
    if whatever in '0123456789':
        return subscriptCodepoint(ord(whatever))
    raise Exception('invalid argument')

def superscriptCodepoint(whatever):
    if whatever in range(10):
        return ord(unicodedata.lookup('SUBSCRIPT ' + whatever))
    if whatever in range(48, 58):
        return ord(unicodedata.lookup('SUBSCRIPT ' + (whatever - 48)))
    if whatever in '0123456789':
        return subscriptCodepoint(ord(whatever))
    raise Exception('invalid argument')

vulgarFractionCodepoints = {
    "1/4": "VULGAR FRACTION ONE QUARTER",
    "1/2": "VULGAR FRACTION ONE HALF",
    "3/4": "VULGAR FRACTION THREE QUARTERS",
    "1/3": "VULGAR FRACTION ONE THIRD",
    "2/3": "VULGAR FRACTION TWO THIRDS",
    "1/5": "VULGAR FRACTION ONE FIFTH",
    "2/5": "VULGAR FRACTION TWO FIFTHS",
    "3/5": "VULGAR FRACTION THREE FIFTHS",
    "4/5": "VULGAR FRACTION FOUR FIFTHS",
    "1/6": "VULGAR FRACTION ONE SIXTH",
    "5/6": "VULGAR FRACTION FIVE SIXTHS",
    "1/7": "VULGAR FRACTION ONE SEVENTH",
    "1/8": "VULGAR FRACTION ONE EIGHTH",
    "3/8": "VULGAR FRACTION THREE EIGHTHS",
    "5/8": "VULGAR FRACTION FIVE EIGHTHS",
    "7/8": "VULGAR FRACTION SEVEN EIGHTHS",
}

# num and denom arguments can be any of the following:
#     48 .. 57
#     0 .. 9
#     '0' .. '9'
def vulgarFractionCodepoint(num, denom):
    if num in range(48, 58):
        num = num - 48
    if denom in range(48, 58):
        denom = denom - 48
    charName = vulgarFractionCodepoints[num + "/" + denom]
    char = unicodedata.lookup(charName)
    return ord(char)
