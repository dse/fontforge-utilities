#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
import os
import sys

sys.path = [os.path.dirname(__file__) + '/../lib'] + sys.path
from glyphlist import GLYPH_LIST_PRINTING
from myfontutils import run_font_coverage_cli

def main():
    run_font_coverage_cli(GLYPH_LIST_PRINTING,
                          "Combined Standard Glyph Lists")

main()
