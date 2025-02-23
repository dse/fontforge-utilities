import unicodedata

NON_PRINTING = [
    'Cc',                       # control
    'Cf',                       # format
    'Cn',                       # unassigned
    'Co',                       # private use
    'Cs',                       # surrogate
    'Zl',                       # line separator
    'Zp',                       # paragraph separator
]

# "official" unicode mappings
CODE_PAGE_437 = [
    0x263a, 0x263b, 0x2665, 0x2666, 0x2663, 0x2660, 0x2022, 0x25d8,
    0x25cb, 0x25d9, 0x2642, 0x2640, 0x266a, 0x266b, 0x263c, 0x25ba,
    0x25c4, 0x2195, 0x203c, 0x00b6, 0x00a7, 0x25ac, 0x21a8, 0x2191,
    0x2193, 0x2192, 0x2190, 0x221f, 0x2194, 0x25b2, 0x25bc, 0x007c,
    0x2302, 0x00c7, 0x00fc, 0x00e9, 0x00e2, 0x00e4, 0x00e0, 0x00e5,
    0x00e7, 0x00ea, 0x00eb, 0x00e8, 0x00ef, 0x00ee, 0x00ec, 0x00c4,
    0x00c5, 0x00c9, 0x00e6, 0x00c6, 0x00f4, 0x00f6, 0x00f2, 0x00fb,
    0x00f9, 0x00ff, 0x00d6, 0x00dc, 0x00a2, 0x00a3, 0x00a5, 0x20a7,
    0x0192, 0x00e1, 0x00ed, 0x00f3, 0x00fa, 0x00f1, 0x00d1, 0x00aa,
    0x00ba, 0x00bf, 0x2310, 0x00ac, 0x00bd, 0x00bc, 0x00a1, 0x00ab,
    0x00bb, 0x2591, 0x2592, 0x2593, 0x2502, 0x2524, 0x2561, 0x2562,
    0x2556, 0x2555, 0x2563, 0x2551, 0x2557, 0x255d, 0x255c, 0x255b,
    0x2510, 0x2514, 0x2534, 0x252c, 0x251c, 0x2500, 0x253c, 0x255e,
    0x255f, 0x255a, 0x2554, 0x2569, 0x2566, 0x2560, 0x2550, 0x256c,
    0x2567, 0x2568, 0x2564, 0x2565, 0x2559, 0x2558, 0x2552, 0x2553,
    0x256b, 0x256a, 0x2518, 0x250c, 0x2588, 0x2584, 0x258c, 0x2590,
    0x2580, 0x03b1, 0x00df, 0x0393, 0x03c0, 0x03a3, 0x03c3, 0x00b5,
    0x03c4, 0x03a6, 0x0398, 0x03a9, 0x03b4, 0x221e, 0x03c6, 0x03b5,
    0x2229, 0x2261, 0x00b1, 0x2265, 0x2264, 0x2320, 0x2321, 0x00f7,
    0x2248, 0x00b0, 0x2219, 0x00b7, 0x221a, 0x207f, 0x00b2, 0x25a0,
    0x00a0
]

# additional unicode mappings for other common use cases
CODE_PAGE_437_SUPPLEMENT = [
    0x266c, 0x00a6, 0x0394, 0x23ae, 0x03b2, 0x03a0, 0x220f, 0x2211,
    0x03bc, 0x2126, 0x00f0, 0x2202, 0x03d5, 0x1d719, 0x2205, 0x2300,
    0x00d8, 0x2208, 0x20ac, 0x017f, 0x2022, 0x00b7, 0x2022, 0x2219,
    0x2713
]

CODE_PAGE_437_ALL = CODE_PAGE_437 + CODE_PAGE_437_SUPPLEMENT

CODE_PAGE_437.sort()
CODE_PAGE_437_SUPPLEMENT.sort()
CODE_PAGE_437_ALL.sort()

CODE_PAGE_437_PRINTING = [
    codepoint for codepoint in CODE_PAGE_437 if
    unicodedata.category(chr(codepoint)) not in NON_PRINTING
]
CODE_PAGE_437_SUPPLEMENT_PRINTING = [
    codepoint for codepoint in CODE_PAGE_437_SUPPLEMENT if
    unicodedata.category(chr(codepoint)) not in NON_PRINTING
]
CODE_PAGE_437_ALL_PRINTING = [
    codepoint for codepoint in CODE_PAGE_437_ALL if
    unicodedata.category(chr(codepoint)) not in NON_PRINTING
]
