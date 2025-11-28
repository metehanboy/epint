# -*- coding: utf-8 -*-

"""
Progress bar utility - Rich kütüphanesi kullanarak Notebook, Python script ve CLI için uyumlu
"""

from typing import Optional
from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.console import Console


def _get_console():
    """Rich Console oluştur - notebook/terminal otomatik algılar"""
    try:
        # Notebook içinde mi kontrol et
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None and ipython.__class__.__name__ == 'ZMQInteractiveShell':
            # Notebook için özel console
            return Console(force_terminal=False, width=100)
    except ImportError:
        pass
    
    # Terminal için varsayılan console
    return Console()


class ProgressBar:
    """Progress bar sınıfı - Rich kullanarak Notebook ve CLI için uyumlu"""
    
    def __init__(self, total: int, desc: str = "İşleniyor"):
        self.total = total
        self.current = 0
        self.desc = desc
        self.progress = None
        self.task_id: Optional[TaskID] = None
        self.console = _get_console()
        
        # Rich Progress oluştur
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeRemainingColumn(),
            console=self.console,
            transient=False,
        )
        
        # Progress'i başlat
        self.progress.__enter__()
        
        # Task ekle
        self.task_id = self.progress.add_task(
            description=desc,
            total=total,
        )
    
    def update(self, n: int = 1):
        """Progress'i güncelle"""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, advance=n)
            self.current = min(self.current + n, self.total)
    
    def set_description(self, desc: str):
        """Açıklamayı güncelle"""
        self.desc = desc
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, description=desc)
    
    def close(self):
        """Progress bar'ı kapat"""
        if self.progress:
            try:
                # Task'ı tamamla
                if self.task_id is not None:
                    self.progress.update(self.task_id, completed=self.total)
                # Progress'i kapat
                self.progress.__exit__(None, None, None)
            except:
                pass


def show_progress(total: int, desc: str = "İşleniyor"):
    """Progress bar context manager"""
    return ProgressBar(total, desc)
