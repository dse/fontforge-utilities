#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
import os
import sys

sys.path = [os.path.dirname(__file__) + '/../lib'] + sys.path
from aglfn import AGLFN_PRINTING
from myfontutils import run_font_coverage_cli

def main():
    run_font_coverage_cli(AGLFN_PRINTING,
                          "Adobe Glyph List for New Fonts")

main()
