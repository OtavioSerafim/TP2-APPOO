"""Definições básicas compartilhadas entre cenas."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import pygame


_IMAGES_DIR = Path(__file__).resolve().parents[1] / "assets" / "images"
_DEFAULT_BACKGROUND_NAME = "default_background.png"


class BaseScene(ABC):
    """Classe base simples para cenas do jogo."""

    def __init__(self, *, background_name: Union[str, Path, None] = None) -> None:
        self._background_source: Optional[pygame.Surface] = None
        self._background_surface: Optional[pygame.Surface] = None
        self._background_size: Optional[tuple[int, int]] = None
        self._background_path: Optional[Path] = None
        self.set_background(background_name)

    def set_background(self, image: Union[str, Path, None]) -> None:
        """Define o arquivo de fundo, usando o padrão quando não fornecido."""
        path = self._resolve_background_path(image)
        self._background_path = path

        if path is None:
            self._background_source = None
            self._background_surface = None
            self._background_size = None
            return

        try:
            self._background_source = pygame.image.load(str(path)).convert()
        except pygame.error:
            self._background_source = None
        self._background_surface = None
        self._background_size = None

    def draw_background(self, surface: pygame.Surface, fallback_color: tuple[int, int, int]) -> None:
        """Desenha o fundo configurado, caindo para uma cor sólida se necessário."""
        width, height = surface.get_size()
        if self._background_source is None:
            surface.fill(fallback_color)
            return

        if self._background_size != (width, height):
            self._background_surface = pygame.transform.smoothscale(
                self._background_source, (width, height)
            )
            self._background_size = (width, height)

        if self._background_surface is not None:
            surface.blit(self._background_surface, (0, 0))
        else:
            surface.fill(fallback_color)

    def _resolve_background_path(self, image: Union[str, Path, None]) -> Optional[Path]:
        """Resolve caminho do arquivo, retornando None se indisponível."""
        candidate: Path

        if image is None:
            candidate = _IMAGES_DIR / _DEFAULT_BACKGROUND_NAME
            return candidate if candidate.exists() else None

        candidate = Path(image)
        if not candidate.is_absolute():
            bundled = _IMAGES_DIR / candidate
            if bundled.exists():
                return bundled

        if candidate.exists():
            return candidate

        return None

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa eventos provenientes do pygame."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Atualiza lógica da cena considerando delta time."""

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Desenha a cena na superfície alvo."""
