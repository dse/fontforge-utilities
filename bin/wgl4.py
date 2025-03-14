#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
import os
import sys

sys.path = [os.path.dirname(__file__) + '/../lib'] + sys.path
from wgl4 import WGL4_PRINTING
from myfontutils import run_font_coverage_cli

def main():
    run_font_coverage_cli(WGL4_PRINTING,
                          "Windows Glyph List version 4")

main()
