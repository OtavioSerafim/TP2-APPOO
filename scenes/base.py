"""Definições básicas compartilhadas entre cenas."""

from abc import ABC, abstractmethod

import pygame


class BaseScene(ABC):
    """Classe base simples para cenas do jogo."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa eventos provenientes do pygame."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Atualiza lógica da cena considerando delta time."""

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Desenha a cena na superfície alvo."""
