# -*- coding: utf-8 -*-

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

