# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Dict, Any


def get_endpoints_dir() -> str:
    return os.path.dirname(__file__)

def list_categories() -> list:
    return [d for d in os.listdir(get_endpoints_dir()) 
            if os.path.isdir(os.path.join(get_endpoints_dir(), d)) and not d.startswith('_')]
