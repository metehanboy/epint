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

"""Progress bar utilities for date range handler"""

try:
    from alive_progress import alive_bar
    ALIVE_PROGRESS_AVAILABLE = True
except ImportError:
    ALIVE_PROGRESS_AVAILABLE = False
    # Fallback: basit bir progress bar simülasyonu
    def alive_bar(total=None, title=None, **kwargs):
        class DummyBar:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def __call__(self, increment=1):
                pass
        return DummyBar()

__all__ = ['alive_bar', 'ALIVE_PROGRESS_AVAILABLE']

