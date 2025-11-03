# -*- coding: utf-8 -*-

import os


def get_resources_dir():
    return os.path.dirname(__file__)


def get_web_agent_config():
    return os.path.join(get_resources_dir(), "web_agent.params.yml")


__all__ = [
    "get_resources_dir",
    "get_web_agent_config",
]
