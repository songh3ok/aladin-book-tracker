#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel serverless function handler
def handler(request, response):
    return app(request, response)
