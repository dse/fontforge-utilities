# class FontWrapper:
#     def __init__(self):
#         self.argparse = None
#         self.font = None
#         self.capHeight = 0
#         self.italicAngle = 0
#         self.fontData = None
#     def setFont(self, font):
#         self.font = font
#     def setFontData(self):
#         self.fontData = getFontData()
#         if self.fontData == None:
#             raise Exception("no .font.json data found in this or any parent directory")
#     def load(self, filename):
#         self.font = fontforge.open(filename)
#         self.fontData = getFontData(filename)
#         if self.fontData == None:
#             raise Exception("no .font.json data found in this or any parent directory")
#     def save(self, filename):
#         if re.search(r'\.sfd$', filename):
#             self.font.save(filename)
#         else:
#             flags = ('opentype',)
#             self.font.generate(filename, flags = flags)

#     def supersubscriptCodepoint(self, foo, superscript = True):
#         cp = self.codepointOf(foo)
#         if (cp >= 48 and cp <= 57):
#             if superscript:
#                 return SUPERSCRIPT_DIGIT_CODEPOINTS[cp - 48]
#             else:
#                 return SUBSCRIPT_DIGIT_CODEPOINTS[cp - 48]
#         elif (cp >= 0 and cp <= 9):
#             if superscript:
#                 return SUPERSCRIPT_DIGIT_CODEPOINTS[cp]
#             else:
#                 return SUBSCRIPT_DIGIT_CODEPOINTS[cp]
#         else:
#             return cp

#     def superscriptCodepoint(self, foo):
#         return self.supersubscriptCodepoint(foo, True)

#     def subscriptCodepoint(self, foo):
#         return self.supersubscriptCodepoint(foo, False)

#     # 0 .. 9 => 0 .. 9
#     def codepointOf(self, foo):
#         try:
#             unicodeString = unicode
#         except NameError:
#             unicodeString = str
#         if type(foo) == unicodeString or type(foo) == str or type(foo) == bytes:
#             if (len(foo) == 1):
#                 return ord(foo)
#             else:
#                 char = unicodedata.lookup(foo)
#                 return ord(char)
#         elif isinstance(foo, int):
#             return foo
#         elif isinstance(foo, float):
#             return int(foo)
#         else:
#             raise TypeError("argument to codepoint must be a string or an integer")

#     # 0 .. 9 => 48 .. 57
#     def codepoint(self, foo):
#         try:
#             unicodeString = unicode
#         except NameError:
#             unicodeString = str
#         if type(foo) == unicodeString or type(foo) == str or type(foo) == bytes:
#             if (len(foo) == 1):
#                 return ord(foo)
#             else:
#                 char = unicodedata.lookup(foo)
#                 return ord(char)
#         elif isinstance(foo, int):
#             if foo >= 0 and foo <= 9:
#                 return foo + 48
#             else:
#                 return foo
#         else:
#             raise TypeError("argument to codepoint must be a string or an integer")

#     def intersect(self, a, b):
#         return list(set(a) & set(b))

#     def italicAngleRad(self, deg):
#         return deg * math.pi / 180

#     def anchorPointTransform(self, anchorPoint, transform):
#         x = anchorPoint[2]
#         y = anchorPoint[3]
#         p = fontforge.point(x, y)
#         p = p.transform(transform)
#         return (anchorPoint[0], anchorPoint[1], p.x, p.y)

#     def italicSlantRatio(self, deg):
#         return math.tan(self.italicAngleRad(deg))

#     def italicSkew(self, deg):
#         return psMat.skew(self.italicAngleRad(deg))

#     def italicUnskew(self, deg):
#         return psMat.inverse(self.italicSkew(deg))

#     def italicShiftLeft(self, deg):
#         return psMat.translate(-self.fontData['capHeight'] / 2 * self.italicSlantRatio(deg), 0)

#     def italicShiftRight(self, deg):
#         return psMat.inverse(self.italicShiftLeft(deg))

#     def italicTransform(self, deg):
#         return psMat.compose(self.italicSkew(deg), self.italicShiftLeft(deg))

#     def italicUntransform(self, deg):
#         return psMat.inverse(self.italicTransform(deg))

#     # for referenced characters in italic and half-italic fonts
#     def referenceTransform(self, ref, glyph, deg):
#         thatglyphname = ref[0]
#         thisglyphname = glyph.glyphname
#         r = ref[1]

#         columnA = "%s's reference to %s:" % (thisglyphname, thatglyphname)
#         columnB = str(r)

#         ri = psMat.inverse(r)

#         result = psMat.identity()
#         result = psMat.compose(result, self.italicShiftRight(deg))
#         result = psMat.compose(result, self.italicUnskew(deg))
#         result = psMat.compose(result, r)
#         result = psMat.compose(result, self.italicSkew(deg))
#         result = psMat.compose(result, self.italicShiftLeft(deg))

#         return (ref[0], result)

#     def makeSuperscriptOrSubscript(self, sourceCodepoint, destCodepoint, superscript = True, placementMethod = 3):
#         SUPERSUBSCRIPT_SCALE                    = self.fontData['superSubScriptScale']
#         SUPERSUBSCRIPT_FRACTION_LINE            = self.fontData['superSubScriptFractionLine']
#         STROKE_WIDTH                            = self.fontData['strokeWidth']
#         SUPERSUBSCRIPT_FRACTION_LINE_SEPARATION = self.fontData['superSubScriptFractionLineSeparation']
#         CAP_HEIGHT                              = self.fontData['capHeight']

#         sourceCodepoint = self.codepoint(sourceCodepoint)
#         destCodepoint   = self.codepoint(destCodepoint)

#         # vcenter = amount to raise raw scaled number to make it vertically centered
#         # vdiff = amount to raise or lower from vcenter

#         if placementMethod == 1:
#             vcenter = (1 - SUPERSUBSCRIPT_SCALE) * SUPERSUBSCRIPT_FRACTION_LINE
#             vdiff = (SUPERSUBSCRIPT_SCALE * SUPERSUBSCRIPT_FRACTION_LINE
#                      + (1 - SUPERSUBSCRIPT_SCALE / 2) * STROKE_WIDTH
#                      + SUPERSUBSCRIPT_FRACTION_LINE_SEPARATION)
#         if placementMethod == 2:
#             vcenter = SUPERSUBSCRIPT_FRACTION_LINE * (1 - SUPERSUBSCRIPT_SCALE)
#             vdiff = CAP_HEIGHT / 2
#         if placementMethod == 3:
#             vcenter = SUPERSUBSCRIPT_FRACTION_LINE * (1 - SUPERSUBSCRIPT_SCALE)
#             vdiff = (1 - SUPERSUBSCRIPT_SCALE / 2) * (CAP_HEIGHT - STROKE_WIDTH)

#         if superscript:
#             vshift = vcenter + vdiff
#         else:
#             vshift = vcenter - vdiff

#         vshiftXform = psMat.translate(0, vshift)

#         self.font.selection.select(sourceCodepoint)
#         self.font.copy()
#         self.font.selection.select(destCodepoint)
#         self.font.paste()

#         destGlyph = self.font.createChar(destCodepoint)
#         destGlyph.transform(psMat.scale(SUPERSUBSCRIPT_SCALE))
#         destGlyph.transform(vshiftXform)

#         additionalbearing = STROKE_WIDTH / 2 * (1 - SUPERSUBSCRIPT_SCALE)

#         destGlyph.transform(psMat.translate(additionalbearing, 0))
#         destGlyph.width = destGlyph.width + additionalbearing

#     def makeSuperscript(self, sourceCodepoint, destCodepoint):
#         self.makeSuperscriptOrSubscript(sourceCodepoint, destCodepoint, True)

#     def makeSubscript(self, sourceCodepoint, destCodepoint):
#         self.makeSuperscriptOrSubscript(sourceCodepoint, destCodepoint, False)

#     def makeVulgarFraction(self, superCodepoint, subCodepoint, destCodepoint):
#         CODEPOINT_FRACTION_LINE = self.fontData['codepointFractionLine']

#         superCodepoint = self.codepoint(superCodepoint)
#         subCodepoint = self.codepoint(subCodepoint)
#         destCodepoint = self.codepoint(destCodepoint)

#         super = self.font.createChar(superCodepoint)
#         sub   = self.font.createChar(subCodepoint)
#         dest  = self.font.createChar(destCodepoint)
#         dest.clear()

#         fractionline = self.font[CODEPOINT_FRACTION_LINE]

#         width = max([
#             super.width,
#             sub.width,
#             fractionline.width
#         ])

#         dest.addReference(super.glyphname,        psMat.translate((width - super.width       ) / 2, 0))
#         dest.addReference(sub.glyphname,          psMat.translate((width - sub.width         ) / 2, 0))
#         dest.addReference(fractionline.glyphname, psMat.translate((width - fractionline.width) / 2, 0))
#         dest.width = width

#     def generateBraille(self, codepoint):
#         font = self.font

#         glyphHeight = font.ascent + font.descent # 2048 or 1024
#         glyphWidth = glyphHeight / 2             # 1024 or 512
#         brailleScale = 0.75
#         dotWidth = int(glyphHeight / 16 * 0.875) # 112 or 56

#         try:
#             char = unichr(codepoint)
#         except NameError:
#             char = chr(codepoint)
#         try:
#             charName = unicodedata.name(char)
#         except ValueError:
#             sys.stderr.write("%d: not a valid codepoint." % codepoint)
#             return

#         matchBlank = re.search(' BLANK$', charName)
#         matchDots = re.search('-([0-9]+)$', charName)
#         if (not matchBlank) and (not matchDots):
#             sys.stderr.write("%d: Glyph name '%s' does not look like a Unicode Braille glyph name." % (codepoint, charName))
#             return
#         if matchDots:
#             dotString = matchDots.group(1)

#         glyph = None
#         if codepoint in font:
#             glyph = font[codepoint]
#             glyph.clear()
#         else:
#             glyph = font.createChar(codepoint)

#         if matchDots:
#             # where dots 1 through 8 are located
#             dotsXX = [0, 0, 0, 1, 1, 1, 0, 1]
#             dotsYY = [0, 1, 2, 0, 1, 2, 3, 3]

#             middleX = int(0.5 + float(glyphWidth) / 2.0)
#             middleY = int(0.5 + (float(font.ascent) - float(abs(font.descent))) / 2)

#             glyph.activeLayer = 'Fore'
#             pen = glyph.glyphPen()
#             for dotNumberChar in dotString:
#                 dotNumber = int(dotNumberChar) - 1
#                 dotXX = dotsXX[dotNumber]
#                 dotYY = dotsYY[dotNumber]
#                 dotX = int(0.5 + (
#                     float(middleX) + (float(dotXX) - 0.5) * float(glyphWidth) / 2 * brailleScale
#                 ))
#                 dotY = int(0.5 + (
#                     float(middleY) - (float(dotYY) - 1.5) * float(glyphHeight) / 4 * brailleScale
#                 ))
#                 circle = fontforge.unitShape(0)
#                 circle.transform(psMat.scale(dotWidth))
#                 circle.transform(psMat.translate(dotX, dotY))
#                 circle.draw(pen)
#             pen = None

#         glyph.width = glyphWidth

#     # Move contours from foreground layer to background layer.
#     # If background layer is not empty, do nothing.
#     def foreToBack(self, glyph):
#         bg = glyph.background
#         fg = glyph.foreground
#         if not bg.isEmpty():
#             return

#         # save anchor points and references
#         glyph.activeLayer = 'Fore'
#         anchorPoints = glyph.anchorPoints
#         references = glyph.layerrefs[1]

#         # draw foreground contours to background
#         glyph.activeLayer = 'Back' # dest
#         pen = glyph.glyphPen(replace = True)
#         glyph.activeLayer = 'Fore' # src
#         glyph.draw(pen)
#         pen = None

#         # erase foreground layer
#         glyph.activeLayer = 'Fore'
#         pen = glyph.glyphPen(replace = True)
#         pen = None

#         # restore anchor points and references
#         glyph.activeLayer = 'Fore'
#         for anchorPoint in anchorPoints:
#             glyph.addAnchorPoint(*anchorPoint)
#         for reference in references:
#             glyph.addReference(reference[0], reference[1])

#     def makeBoxDrawingHeavier(self, glyph):
#         font = glyph.font
#         if not (glyph.unicode >= 0x2500 and glyph.unicode <= 0x254f) or (glyph.unicode >= 0x2574 and glyph.unicode <= 0x257f):
#             return

#         middleX = int(0.5 + 1.0 * glyph.width / 2)
#         middleY = int(0.5 + 1.0 * (font.ascent - abs(font.descent)) / 2)
#         backLayer = glyph.layers['Back']

#         modifyBackLayer = False
#         contours = []
#         newContours = []

#         for contour in backLayer:
#             contours += [contour]
#             newContour = fontforge.contour()
#             for point in contour:
#                 if point.x == middleX - 48:
#                     modifyBackLayer = True
#                     point.x = middleX - 96
#                 if point.x == middleX + 48:
#                     modifyBackLayer = True
#                     point.x = middleX + 96
#                 if point.y == middleY - 48:
#                     modifyBackLayer = True
#                     point.y = middleY - 96
#                 if point.y == middleY + 48:
#                     modifyBackLayer = True
#                     point.y = middleY + 96
#                 newContour += point
#             newContours += [newContour]

#         if modifyBackLayer:
#             glyph.layers['Back'] = fontforge.layer()
#             for contour in newContours:
#                 glyph.layers['Back'] += contour
#             backLayer = glyph.layers['Back']

#     # Copy contours from background to foreground, and stroke them.
#     def strokeGlyph(self, glyph):
#         strokeWidth = self.fontData['strokeWidth']
#         font = glyph.font

#         # only fg should have layerrefs
#         glyph.layerrefs[0] = ()

#         bg = glyph.background
#         fg = glyph.foreground
#         if bg.isEmpty():
#             return

#         glyph.round()

#         savedWidth = glyph.width

#         # save anchor points and references
#         glyph.activeLayer = 'Fore'
#         anchorPoints = glyph.anchorPoints
#         references = glyph.layerrefs[1]

#         copyLayer(glyph, src = 'Back', dest = 'Fore')

#         if (glyph.unicode >= 0x2500 and glyph.unicode < 0x2600 and not (glyph.unicode >= 0x2571 and glyph.unicode <= 0x2573)):
#             # Box Drawing Characters
#             lineCap = 'butt'
#             lineJoin = 'round'
#         else:
#             lineCap = 'round'
#             lineJoin = 'round'

#         glyph.activeLayer = 'Fore'
#         if font.fontname == 'RoutedGothic':
#             if glyph.unicode in [0x26, 0x34, 0x36, 0x39, 0x52, 0x65, 0xae, 0xe6,
#                                  0x2074, 0x2076, 0x2079,
#                                  0x2084, 0x2086, 0x2089]:
#                 glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
#                 glyph.removeOverlap()
#             else:
#                 glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
#                 glyph.removeOverlap()
#         elif font.fontname == 'DSETypewriter':
#             if glyph.unicode in [0x3b1]:
#                 glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
#                 glyph.removeOverlap()
#                 sys.stderr.write("alpha\n");
#             else:
#                 glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
#                 glyph.removeOverlap()
#         else:
#             glyph.stroke('circular', strokeWidth, lineCap, lineJoin)
#             glyph.removeOverlap()

#         glyph.width = savedWidth

#         # restore anchor points and references
#         glyph.activeLayer = 'Fore'
#         for anchorPoint in anchorPoints:
#             glyph.addAnchorPoint(*anchorPoint)
#         for reference in references:
#             glyph.addReference(reference[0], reference[1])

#     def clipGlyph(self, glyph):
#         font = glyph.font
#         clipContour = fontforge.contour()
#         clipContour.moveTo(0, font.ascent)
#         clipContour.lineTo(glyph.width, font.ascent)
#         clipContour.lineTo(glyph.width, -font.descent)
#         clipContour.lineTo(0, -font.descent)
#         clipContour.closed = True
#         glyph.layers['Fore'] += clipContour
#         glyph.intersect()
#         glyph.addExtrema()

#     def condense(self, scalex):
#         font = self.font
#         if scalex != 1:
#             for lookupName in font.gpos_lookups:
#                 for subtableName in font.getLookupSubtables(lookupName):
#                     if font.isKerningClass(subtableName):
#                         kc = font.getKerningClass(subtableName)
#                         offsets = kc[2]
#                         newOffsets = tuple([int(0.5 + o * scalex) for o in offsets])
#                         font.alterKerningClass(subtableName, kc[0], kc[1], newOffsets)
#                         kc = font.getKerningClass(subtableName)

#             font.selection.all()
#             font.transform(psMat.scale(scalex, 1))

#             for lookupName in font.gpos_lookups:
#                 for subtableName in font.getLookupSubtables(lookupName):
#                     if font.isKerningClass(subtableName):
#                         kc = font.getKerningClass(subtableName)

#     def italicize(self, italicDeg):
#         font = self.font
#         for glyph in font.glyphs():
#             width = glyph.width
#             for name in glyph.layers:
#                 layer = glyph.layers[name]
#                 layer.transform(self.italicTransform(italicDeg))
#                 glyph.layers[name] = layer
#                 glyph.width = width
#             glyph.activeLayer = 'Fore'
#             glyph.anchorPoints = [
#                 self.anchorPointTransform(p, self.italicTransform(italicDeg))
#                 for p in glyph.anchorPoints
#             ]
#             glyph.references = [
#                 self.referenceTransform(r, glyph, italicDeg)
#                 for r in glyph.references
#             ]
#             glyph.activeLayer = 'Back'
#             glyph.anchorPoints = []
#             glyph.references = []

#     def generate(self,
#                  fontName,
#                  familyName,
#                  weightName,
#                  italicDeg = 0,
#                  italicName = "",
#                  condensedScale = 1,
#                  condensedName = "",
#                  generateSuperAndSubscripts = True,
#                  generateSuperAndSubscriptsMethod = 3,
#                  familyNameSuffix = "",
#                  variantCount = None):
#         self.fontData = getFontData()

#         ITALIC_ANGLE_DEG   = getCoalesce(self.fontData, 'italicAngleDeg')
#         DIST_SFD_DIRECTORY = getCoalesce(self.fontData, 'distSFDDirectory')
#         DIST_TTF_DIRECTORY = getCoalesce(self.fontData, 'distTTFDirectory')
#         fontFileBasename   = getCoalesce(self.fontData, 'fontFileBasename')
#         sourceFilename     = getCoalesce(self.fontData, 'sourceFilename')
#         FRACTION_LINE_EXTRA_WIDTH = getCoalesce(self.fontData, 'fractionLineExtraWidth')
#         CODEPOINT_FRACTION_LINE   = getCoalesce(self.fontData, 'codepointFractionLine')
#         STROKE_WIDTH              = getCoalesce(self.fontData, 'strokeWidth')
#         FRACTION_LINE_BEARING     = getCoalesce(self.fontData, 'fractionLineBearing')
#         SUPERSUBSCRIPT_FRACTION_LINE = getCoalesce(self.fontData, 'superSubScriptFractionLine')
#         SUPERSUBSCRIPT_FRACTION_LINE_SEPARATION = getCoalesce(self.fontData, 'superSubScriptFractionLineSeparation')

#         font = self.font = fontforge.open(sourceFilename)

#         if generateSuperAndSubscripts:
#             for digit in '0123456789':
#                 codepoint = ord(digit) # 48..57
#                 superscriptCodepoint = self.subscriptCodepoint(codepoint)
#                 subscriptCodepoint = self.subscriptCodepoint(codepoint)
#                 self.makeSuperscript(codepoint, superscriptCodepoint)
#                 self.makeSubscript(codepoint, subscriptCodepoint)

#             superDigitGlyphs = [
#                 font[cp]
#                 for cp in SUPERSCRIPT_DIGIT_CODEPOINTS
#             ]
#             fractionlinewidth = max([g.width for g in superDigitGlyphs]) + FRACTION_LINE_EXTRA_WIDTH

#             fractionline = font.createChar(CODEPOINT_FRACTION_LINE)
#             pen = fractionline.glyphPen()
#             pen.moveTo((STROKE_WIDTH / 2 + FRACTION_LINE_BEARING,
#                         SUPERSUBSCRIPT_FRACTION_LINE))
#             pen.lineTo((fractionlinewidth - STROKE_WIDTH / 2 - FRACTION_LINE_BEARING,
#                         SUPERSUBSCRIPT_FRACTION_LINE))
#             pen.endPath()           # leave path open
#             pen = None              # finalize
#             fractionline.width = fractionlinewidth

#             for vf in VULGAR_FRACTIONS:
#                 numerator   = vf['numerator']
#                 denominator = vf['denominator']
#                 fraction    = vf['codepoint']

#                 numerator   = self.superscriptCodepoint(numerator)
#                 denominator = self.subscriptCodepoint(denominator)
#                 fraction    = self.codepoint(fraction)
#                 self.makeVulgarFraction(numerator, denominator, fraction)

#         # condense kerning pairs if needed

#         if condensedScale != 1:
#             self.condense(condensedScale)

#         for glyph in font.glyphs():
#             glyph.manualHints = False

#         for glyph in font.glyphs():
#             if len(glyph.references) == 2:
#                 glyphname1 = glyph.references[0][0]
#                 glyphname2 = glyph.references[1][0]
#                 g1 = font[glyphname1]
#                 g2 = font[glyphname2]
#                 g1BaseAps = tuple([ap[0] for ap in g1.anchorPoints if ap[1] == "base"])
#                 g1MarkAps = tuple([ap[0] for ap in g1.anchorPoints if ap[1] == "mark"])
#                 g2BaseAps = tuple([ap[0] for ap in g2.anchorPoints if ap[1] == "base"])
#                 g2MarkAps = tuple([ap[0] for ap in g2.anchorPoints if ap[1] == "mark"])
#                 i1 = self.intersect(g1BaseAps, g2MarkAps)
#                 i2 = self.intersect(g2BaseAps, g1MarkAps)
#                 if len(i1) or len(i2):
#                     glyph.build()

#         if italicDeg:
#             self.italicize(italicDeg)

#         for glyph in font.glyphs():
#             self.strokeGlyph(glyph)

#         # call build() on glyphs that reference two glyphs if anchor
#         # points would be used
#         # for glyph in font.glyphs():
#         #     built = False
#         #     if len(glyph.references) == 2:
#         #         glyphname1 = glyph.references[0][0]
#         #         glyphname2 = glyph.references[1][0]
#         #         g1 = font[glyphname1]
#         #         g2 = font[glyphname2]
#         #         g1BaseAps = tuple([ap[0] for ap in g1.anchorPoints if ap[1] == "base"])
#         #         g1MarkAps = tuple([ap[0] for ap in g1.anchorPoints if ap[1] == "mark"])
#         #         g2BaseAps = tuple([ap[0] for ap in g2.anchorPoints if ap[1] == "base"])
#         #         g2MarkAps = tuple([ap[0] for ap in g2.anchorPoints if ap[1] == "mark"])
#         #         i1 = self.intersect(g1BaseAps, g2MarkAps)
#         #         i2 = self.intersect(g2BaseAps, g1MarkAps)
#         #         if len(i1) or len(i2):
#         #             glyph.build()
#         #             built = True
#         #     if not built:
#         #         if italicDeg:
#         #             glyph.references = [
#         #                 self.referenceTransform(r, glyph, italicDeg)
#         #                 for r in glyph.references
#         #             ]

#         font.strokedfont = False

#         font.fontname    = fontName
#         font.familyname  = familyName
#         font.fullname    = familyName
#         font.weight      = weightName
#         font.italicangle = italicDeg
#         basename         = fontFileBasename

#         familyNameSuffix = re.sub(r'^\s+', '', familyNameSuffix)
#         familyNameSuffix = re.sub(r'\s+$', '', familyNameSuffix)

#         if condensedScale != 1:
#             font.fontname    = font.fontname   +       condensedName.replace("-", "").replace(" ", "")
#             font.fullname    = font.fullname   + " " + condensedName.replace("-", " ")
#             basename         = basename        + "-" + condensedName.lower().replace(" ", "-")

#         if italicDeg:
#             font.italicangle = -ITALIC_ANGLE_DEG
#             font.fontname    = font.fontname   + "-" + italicName.replace(" ", "-")
#             font.fullname    = font.fullname   + " " + italicName.replace("-", " ")
#             basename         = basename        + "-" + italicName.lower().replace(" ", "-")

#         if familyNameSuffix != "":
#             font.familyname  = font.familyname + " " + familyNameSuffix

#         sfdFilename = DIST_SFD_DIRECTORY + "/" + basename + ".sfd"
#         ttfFilename = DIST_TTF_DIRECTORY + "/" + basename + ".ttf"

#         sfdDir = os.path.dirname(sfdFilename)
#         ttfDir = os.path.dirname(ttfFilename)
#         if not os.path.exists(sfdDir):
#             os.makedirs(sfdDir)
#         if not os.path.exists(ttfDir):
#             os.makedirs(ttfDir)

#         print("Saving " + sfdFilename + " ...")
#         font.save(sfdFilename)
#         print("Saving " + ttfFilename + " ...")
#         if font.fontname == 'RoutedGothic':
#             font.generate(ttfFilename, flags=())
#         else:
#             font.generate(ttfFilename, flags=("opentype"))

#         font.close()
#         self.font = None
