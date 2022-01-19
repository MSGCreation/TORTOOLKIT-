#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = "1.0.0"
__author__ = "Sam"
#
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(),logging.FileHandler("torlog.txt")]
)

from .core.varholdern import VarHolder
import time

uptime = time.time()
to_del = []
SessionVars = VarHolder()