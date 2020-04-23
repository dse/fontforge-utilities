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
