# -*- coding: utf-8 -*-

import os
from typing import Dict, Any


def get_endpoints_dir() -> str:
    return os.path.dirname(__file__)

def list_categories() -> list:
    return [d for d in os.listdir(get_endpoints_dir()) 
            if os.path.isdir(os.path.join(get_endpoints_dir(), d)) and not d.startswith('_')]
