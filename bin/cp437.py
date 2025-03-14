#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
import os
import sys

sys.path = [os.path.dirname(__file__) + '/../lib'] + sys.path
from codepage437 import CODE_PAGE_437_PRINTING
from myfontutils import run_font_coverage_cli

def main():
    run_font_coverage_cli(CODE_PAGE_437_PRINTING,
                          "IBM Code Page 437")

main()
