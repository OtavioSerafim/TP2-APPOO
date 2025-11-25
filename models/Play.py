"""Modelo de acesso à tabela ``plays``."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from .Model import Model


def _normalize_datetime(value: Any) -> str:
	if isinstance(value, datetime):
		return value.replace(microsecond=0).isoformat(sep=" ")
	if isinstance(value, str) and value.strip():
		return value.strip()
	raise ValueError("O campo 'played_at' deve ser datetime ou string não vazia.")


def _ensure_int(value: Any, field: str, minimum: int | None = None) -> int:
	if isinstance(value, bool):
		raise ValueError(f"O campo '{field}' deve ser um inteiro, não booleano.")
	if not isinstance(value, int):
		raise ValueError(f"O campo '{field}' deve ser um inteiro.")
	if minimum is not None and value < minimum:
		raise ValueError(f"O campo '{field}' deve ser maior ou igual a {minimum}.")
	return value


class Play(Model):
	"""Gerencia registros de partidas jogadas."""

	_COLUMNS = (
		"id",
		"played_at",
		"music_name",
		"score",
		"player_id",
		"errors",
		"perfect_hits",
		"good_hits",
		"bad_hits",
	)

	_COUNTER_FIELDS = ("errors", "perfect_hits", "good_hits", "bad_hits")

	def __init__(self, connection) -> None:
		super().__init__(connection, table_name="plays", columns=self._COLUMNS)

	# ------------------------------------------------------------------
	# Preparação de payloads
	# ------------------------------------------------------------------
	def prepare_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		payload: Dict[str, Any] = {}

		payload["played_at"] = _normalize_datetime(data.get("played_at"))

		music_name = data.get("music_name")
		if not isinstance(music_name, str) or not music_name.strip():
			raise ValueError("O campo 'music_name' deve ser uma string não vazia.")
		payload["music_name"] = music_name.strip()

		payload["score"] = _ensure_int(data.get("score"), "score", minimum=0)
		payload["player_id"] = _ensure_int(data.get("player_id"), "player_id", minimum=1)

		for field in self._COUNTER_FIELDS:
			value = data.get(field, 0)
			payload[field] = _ensure_int(value, field, minimum=0)

		return payload

	def prepare_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		payload: Dict[str, Any] = {}

		if "played_at" in data:
			payload["played_at"] = _normalize_datetime(data["played_at"])

		if "music_name" in data:
			music_name = data["music_name"]
			if not isinstance(music_name, str) or not music_name.strip():
				raise ValueError("O campo 'music_name' deve ser uma string não vazia.")
			payload["music_name"] = music_name.strip()

		if "score" in data:
			payload["score"] = _ensure_int(data["score"], "score", minimum=0)

		if "player_id" in data:
			payload["player_id"] = _ensure_int(data["player_id"], "player_id", minimum=1)

		for field in self._COUNTER_FIELDS:
			if field in data:
				payload[field] = _ensure_int(data[field], field, minimum=0)

		return payload

	# ------------------------------------------------------------------
	# Utilidades
	# ------------------------------------------------------------------
	def for_player(self, player_id: int) -> Iterable[Any]:
		"""Retorna todas as partidas relacionadas a um jogador específico."""
		player_id = _ensure_int(player_id, "player_id", minimum=1)
		query = (
			"SELECT "
			+ ", ".join(self._COLUMNS)
			+ " FROM plays WHERE player_id = ? ORDER BY played_at DESC"
		)
		self.cursor.execute(query, (player_id,))
		return self.cursor.fetchall()

	def latest(self, limit: int = 10) -> Iterable[Any]:
		"""Retorna as últimas partidas registradas."""
		limit = _ensure_int(limit, "limit", minimum=1)
		query = (
			"SELECT "
			+ ", ".join(self._COLUMNS)
			+ " FROM plays ORDER BY played_at DESC LIMIT ?"
		)
		self.cursor.execute(query, (limit,))
		return self.cursor.fetchall()

	def leaderboard_for_music(self, music_name: str, limit: int = 10) -> Iterable[Any]:
		"""Retorna as melhores partidas para uma música específica."""
		if not isinstance(music_name, str) or not music_name.strip():
			raise ValueError("Informe um nome de música válido.")
		limit = _ensure_int(limit, "limit", minimum=1)
		query = (
			"SELECT "
			"plays.id, plays.played_at, plays.music_name, plays.score, plays.player_id, "
			"plays.errors, plays.perfect_hits, plays.good_hits, plays.bad_hits, "
			"COALESCE(player.name, 'Jogador #' || plays.player_id) AS player_name "
			"FROM plays "
			"LEFT JOIN player ON player.id = plays.player_id "
			"WHERE plays.music_name = ? "
			"ORDER BY plays.score DESC, plays.played_at ASC "
			"LIMIT ?"
		)
		self.cursor.execute(query, (music_name.strip(), limit))
		return self.cursor.fetchall()

	def best_for_player_and_music(self, player_id: int, music_name: str) -> Optional[Any]:
		"""Retorna a melhor partida de um jogador para a música informada."""
		player_id = _ensure_int(player_id, "player_id", minimum=1)
		if not isinstance(music_name, str) or not music_name.strip():
			raise ValueError("Informe um nome de música válido.")
		query = (
			"SELECT "
			"plays.id, plays.played_at, plays.music_name, plays.score, plays.player_id, "
			"plays.errors, plays.perfect_hits, plays.good_hits, plays.bad_hits, "
			"COALESCE(player.name, 'Jogador #' || plays.player_id) AS player_name "
			"FROM plays "
			"LEFT JOIN player ON player.id = plays.player_id "
			"WHERE plays.music_name = ? AND plays.player_id = ? "
			"ORDER BY plays.score DESC, plays.played_at ASC "
			"LIMIT 1"
		)
		self.cursor.execute(query, (music_name.strip(), player_id))
		return self.cursor.fetchone()


__all__ = ["Play"]
