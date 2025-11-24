"""Facilita importações das cenas disponíveis."""

from .add_music import AddMusicScene
from .base import BaseScene
from .menu import MenuScene
from .music_select import MusicSelectScene

__all__ = ["BaseScene", "MenuScene", "MusicSelectScene", "AddMusicScene"]
