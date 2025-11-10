"""Contexto compartilhado para acesso aos modelos persistentes."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

from .Model import Model
from .Play import Play
from .Player import Player


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "Database" / "app.db"


class Models:
    """Mantém uma conexão SQLite e expõe modelos tipados."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        self._models: Dict[str, Model] = {
            "player": Player(self._connection),
            "play": Play(self._connection),
        }

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def get(self, name: str) -> Model:
        alias = name.lower()
        if alias not in self._models:
            raise KeyError(f"Modelo '{name}' não registrado.")
        return self._models[alias]

    @property
    def player(self) -> Player:
        return self._models["player"]

    @property
    def play(self) -> Play:
        return self._models["play"]

    def close(self) -> None:
        self._connection.close()


__all__ = ["Models"]