import re

class UnicodeMapping:
    # example: https://www.unicode.org/Public/MAPPINGS/VENDORS/MICSFT/PC/CP437.TXT
    @classmethod
    def init(cls, text):
        cls.codepoints = []
        pattern = re.compile(r'0x([0-9A-Fa-f]+)\s+0x([0-9A-Fa-f]+)')
        for line in re.split(r'\r\n?|\n', text):
            m = pattern.match(line)
            if m:
                (cp437, unicode) = m.groups()
                cp437 = int(cp437, 16)
                unicode = int(unicode, 16)
                cls.codepoints.append(unicode)
        cls.codepoints = list(set(cls.codepoints)) # uniq
        cls.codepoints.sort()
