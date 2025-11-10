"""Modelo de acesso à tabela ``player``."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .Model import Model


class Player(Model):
	"""Gerencia operações de CRUD para jogadores."""

	def __init__(self, connection) -> None:
		super().__init__(connection, table_name="player", columns=("id", "name"))

	def prepare_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		payload = {}

		name = data.get("name")
		if not isinstance(name, str) or not name.strip():
			raise ValueError("O nome do jogador deve ser uma string não vazia.")
		payload["name"] = name.strip()

		return payload

	def prepare_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		payload: Dict[str, Any] = {}
		if "name" in data:
			name = data["name"]
			if not isinstance(name, str) or not name.strip():
				raise ValueError("O nome do jogador deve ser uma string não vazia.")
			payload["name"] = name.strip()

		return payload

	def get_by_name(self, name: str) -> Optional[Any]:
		"""Busca um jogador pelo nome exato."""
		if not isinstance(name, str) or not name.strip():
			raise ValueError("Informe um nome válido para busca.")

		query = "SELECT id, name FROM player WHERE name = ?"
		self.cursor.execute(query, (name.strip(),))
		return self.cursor.fetchone()


__all__ = ["Player"]
