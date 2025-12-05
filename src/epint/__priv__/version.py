# -*- coding: utf-8 -*-

from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def get_version() -> str:
    """pyproject.toml'dan versiyonu oku"""
    if tomllib is None:
        return "0.1.0"
    
    try:
        # __file__ -> __priv__ -> epint -> src -> epint (root)
        pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                config = tomllib.load(f)
                return config["project"]["version"]
    except Exception:
        pass
    return "0.1.0"

