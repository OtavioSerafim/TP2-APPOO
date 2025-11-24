"""Cena responsável por cadastrar novas músicas a partir de um arquivo ZIP."""

from __future__ import annotations

import pathlib
import shutil
import tempfile
import zipfile

import pygame

import tkinter as tk
from tkinter import filedialog
from .base import BaseScene
from utils.buttons import Button, ButtonTheme
from utils.constants import (
    COLOR_BACKGROUND,
    COLOR_ERROR,
    COLOR_PRIMARY,
    COLOR_TEXT_MUTED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from utils.input_field import InputField


UI_CONFIG = {
    "font_sizes": {
        "title": 74,
        "subtitle": 34,
        "input": 38,
        "label": 28,
        "button": 40,
        "feedback": 32,
    },
    "placeholders": {
        "name": "Exemplo: Nova Música",
        "zip": "Exemplo: C:/caminho/arquivo.zip",
    },
    "layout": {
        "title_ratio": 0.18,
        "title_min_y": 70,
        "subtitle_gap": 52,
        "fields_offset": 50,
        "field_max_width": 540,
        "field_width_ratio": 0.65,
        "field_height": 64,
        "field_spacing": 32,
        "select_max_width": 320,
        "select_width_ratio": 0.5,
        "select_height": 58,
        "select_gap": 20,
        "action_width": 200,
        "action_height": 62,
        "action_spacing": 28,
        "action_gap": 40,
        "feedback_gap": 120,
        "feedback_bottom_margin": 60,
    },
}


class AddMusicScene(BaseScene):
    """Tela que recebe dados do usuário e importa uma nova música."""

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        font_sizes = UI_CONFIG["font_sizes"]
        self.title_font = pygame.font.Font(None, font_sizes["title"])
        self.subtitle_font = pygame.font.Font(None, font_sizes["subtitle"])
        self.input_font = pygame.font.Font(None, font_sizes["input"])
        self.label_font = pygame.font.Font(None, font_sizes["label"])
        self.button_font = pygame.font.Font(None, font_sizes["button"])
        self.feedback_font = pygame.font.Font(None, font_sizes["feedback"])

        self.theme = ButtonTheme()

        self.name_field = InputField(
            label="Nome da música",
            placeholder=UI_CONFIG["placeholders"]["name"],
            rect=pygame.Rect(0, 0, 0, 0),
            font=self.input_font,
            label_font=self.label_font,
        )
        self.zip_field = InputField(
            label="Arquivo ZIP",
            placeholder=UI_CONFIG["placeholders"]["zip"],
            rect=pygame.Rect(0, 0, 0, 0),
            font=self.input_font,
            label_font=self.label_font,
        )
        self.fields: list[InputField] = [self.name_field, self.zip_field]
        self._focused_index = 0
        self._set_focus(0)

        self.buttons = self._build_buttons()
        self.select_button = Button(
            pygame.Rect(0, 0, 0, 0),
            "Selecionar arquivo",
            self.button_font,
            self._on_select_zip,
            self.theme,
        )
        self.feedback_message = ""
        self.feedback_is_error = False

        layout_cfg = UI_CONFIG["layout"]
        title_y = max(int(SCREEN_HEIGHT * layout_cfg["title_ratio"]), layout_cfg["title_min_y"])
        subtitle_y = title_y + layout_cfg["subtitle_gap"]

        self._title_pos = (SCREEN_WIDTH // 2, title_y)
        self._subtitle_pos = (SCREEN_WIDTH // 2, subtitle_y)
        self._feedback_y = SCREEN_HEIGHT - layout_cfg["feedback_bottom_margin"]
        self._layout_size = (0, 0)
        self._apply_layout(SCREEN_WIDTH, SCREEN_HEIGHT)

    def _build_buttons(self) -> list[Button]:
        """Configura botões da cena."""
        actions = [
            ("Importar", self._on_submit),
            ("Cancelar", self._on_cancel),
        ]
        return [
            Button(pygame.Rect(0, 0, 0, 0), label, self.button_font, callback, self.theme)
            for (label, callback) in actions
        ]

    def _apply_layout(self, width: int, height: int) -> None:
        """Reposiciona campos e botões conforme o tamanho da janela."""
        layout_cfg = UI_CONFIG["layout"]
        field_width = min(layout_cfg["field_max_width"], int(width * layout_cfg["field_width_ratio"]))
        field_height = layout_cfg["field_height"]
        field_spacing = layout_cfg["field_spacing"]

        title_y = max(int(height * layout_cfg["title_ratio"]), layout_cfg["title_min_y"])
        subtitle_y = title_y + layout_cfg["subtitle_gap"]
        start_y = subtitle_y + layout_cfg["fields_offset"]

        for index, field in enumerate(self.fields):
            rect = pygame.Rect(0, 0, field_width, field_height)
            rect.centerx = width // 2
            rect.y = start_y + index * (field_height + field_spacing)
            field.set_rect(rect)

        select_button_width = min(layout_cfg["select_max_width"], int(width * layout_cfg["select_width_ratio"]))
        select_button_height = layout_cfg["select_height"]
        select_rect = pygame.Rect(0, 0, select_button_width, select_button_height)
        select_rect.centerx = width // 2
        select_rect.y = self.zip_field.rect.bottom + layout_cfg["select_gap"]
        self.select_button.rect = select_rect

        button_width = layout_cfg["action_width"]
        button_height = layout_cfg["action_height"]
        button_spacing = layout_cfg["action_spacing"]
        buttons_total_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * button_spacing
        start_x = width // 2 - buttons_total_width // 2
        buttons_y = self.select_button.rect.bottom + layout_cfg["action_gap"]

        for index, button in enumerate(self.buttons):
            rect = pygame.Rect(
                start_x + index * (button_width + button_spacing),
                buttons_y,
                button_width,
                button_height,
            )
            button.rect = rect

        self._title_pos = (width // 2, title_y)
        self._subtitle_pos = (width // 2, subtitle_y)
        self._feedback_y = min(
            height - layout_cfg["feedback_bottom_margin"],
            buttons_y + layout_cfg["feedback_gap"],
        )
        self._layout_size = (width, height)

    def _set_focus(self, index: int) -> None:
        """Define qual campo de texto está com foco."""
        self._focused_index = index
        for idx, field in enumerate(self.fields):
            field.set_active(idx == index)

    def _clear_feedback(self) -> None:
        """Remove mensagens temporárias da interface."""
        self.feedback_message = ""
        self.feedback_is_error = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Distribui eventos entre campos e botões."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_cancel()
                return
            if event.key == pygame.K_TAB:
                direction = -1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                new_index = (self._focused_index + direction) % len(self.fields)
                self._set_focus(new_index)
                return
            if event.key == pygame.K_RETURN:
                self._on_submit()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, field in enumerate(self.fields):
                if field.rect.collidepoint(event.pos):
                    self._set_focus(index)
                    break

        text_changed = False
        for field in self.fields:
            if field.handle_event(event):
                text_changed = True
        if text_changed:
            self._clear_feedback()

        self.select_button.handle_event(event)
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        """Atualiza campos ativos."""
        changed = False
        for field in self.fields:
            field.update(dt)
            if field.poll_text_changed():
                changed = True
        if changed:
            self._clear_feedback()

    def render(self, surface: pygame.Surface) -> None:
        """Desenha textos, campos e botões."""
        width, height = surface.get_size()
        if (width, height) != self._layout_size:
            self._apply_layout(width, height)

        self.draw_background(surface, COLOR_BACKGROUND)

        title = self.title_font.render("Adicionar Música", True, COLOR_PRIMARY)
        surface.blit(title, title.get_rect(center=self._title_pos))

        subtitle = self.subtitle_font.render(
            "Informe um nome e selecione o arquivo ZIP da música.",
            True,
            COLOR_TEXT_MUTED,
        )
        surface.blit(subtitle, subtitle.get_rect(center=self._subtitle_pos))

        for field in self.fields:
            field.draw(surface)

        self.select_button.draw(surface)
        for button in self.buttons:
            button.draw(surface)

        if self.feedback_message:
            color = COLOR_ERROR if self.feedback_is_error else COLOR_PRIMARY
            feedback_surface = self.feedback_font.render(self.feedback_message, True, color)
            feedback_rect = feedback_surface.get_rect()
            feedback_rect.center = (width // 2, self._feedback_y)
            surface.blit(feedback_surface, feedback_rect)

    def _on_select_zip(self) -> None:
        """Abre o seletor de arquivos do sistema para escolher um ZIP."""
        if tk is None or filedialog is None:
            self._set_feedback("tkinter não está disponível nesta instalação.", is_error=True)
            return

        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except tk.TclError:
            pass

        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo ZIP da música",
            filetypes=[("Arquivos ZIP", "*.zip")],
        )
        root.destroy()

        if not file_path:
            return

        self.zip_field.set_text(file_path)
        if not self.name_field.text.strip():
            suggested_name = pathlib.Path(file_path).stem.replace("_", " ").strip()
            if suggested_name:
                self.name_field.set_text(suggested_name)

        self._clear_feedback()
        self._set_focus(1)

    def _on_submit(self) -> None:
        """Valida entrada e tenta importar a música."""
        name = self.name_field.text.strip()
        zip_text = self.zip_field.text.strip().strip('"')

        if not name:
            self._set_feedback("Informe um nome para a música.", is_error=True)
            return

        if not zip_text:
            self._set_feedback("Selecione o arquivo ZIP.", is_error=True)
            return

        zip_path = pathlib.Path(zip_text).expanduser()
        if not zip_path.is_file():
            self._set_feedback("Arquivo ZIP não encontrado.", is_error=True)
            return

        if zip_path.suffix.lower() != ".zip":
            self._set_feedback("Selecione um arquivo com extensão .zip.", is_error=True)
            return

        sanitized_name = self._sanitize_name(name)
        if not sanitized_name:
            self._set_feedback("Nome inválido após sanitização.", is_error=True)
            return

        target_dir = pathlib.Path("musics") / sanitized_name
        if target_dir.exists():
            self._set_feedback("Já existe uma música com esse nome.", is_error=True)
            return

        try:
            self._import_song(zip_path, target_dir)
        except ValueError as exc:
            self._set_feedback(str(exc), is_error=True)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"Erro ao importar música: {exc}")
            self._set_feedback("Erro inesperado ao importar a música.", is_error=True)
            return

        self._set_feedback("Música importada com sucesso!", is_error=False)
        self._reset_form()

    def _import_song(self, zip_path: pathlib.Path, target_dir: pathlib.Path) -> None:
        """Descompacta arquivo ZIP e copia CSV/MP3 para o diretório de músicas."""
        target_dir.parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                with zipfile.ZipFile(zip_path, "r") as archive:
                    archive.extractall(tmp_dir)
            except zipfile.BadZipFile as exc:
                raise ValueError("Arquivo ZIP inválido.") from exc

            extracted_root = pathlib.Path(tmp_dir)
            csv_files = [path for path in extracted_root.rglob("*") if path.is_file() and path.suffix.lower() == ".csv"]
            mp3_files = [path for path in extracted_root.rglob("*") if path.is_file() and path.suffix.lower() == ".mp3"]

            if not csv_files or not mp3_files:
                raise ValueError("O ZIP precisa conter ao menos um .csv e um .mp3.")

            target_dir.mkdir(parents=True, exist_ok=False)
            try:
                csv_source = csv_files[0]
                mp3_source = mp3_files[0]
                shutil.copy2(csv_source, target_dir / "map.csv")
                shutil.copy2(mp3_source, target_dir / "audio.mp3")
            except Exception:
                if target_dir.exists():
                    shutil.rmtree(target_dir, ignore_errors=True)
                raise ValueError("Falha ao copiar arquivos para a pasta da música.")

    def _set_feedback(self, message: str, *, is_error: bool) -> None:
        """Exibe mensagem temporária ao usuário."""
        self.feedback_message = message
        self.feedback_is_error = is_error

    def _sanitize_name(self, raw_name: str) -> str:
        """Gera nome de pasta seguro para gravar a música."""
        allowed = [ch if ch.isalnum() or ch in (" ", "-", "_") else "" for ch in raw_name]
        sanitized = "".join(allowed).strip()
        sanitized = sanitized.replace(" ", "_")
        return sanitized[:60]

    def _reset_form(self) -> None:
        """Limpa campos e reposiciona o foco após sucesso."""
        self.name_field.clear(silent=True)
        self.zip_field.clear(silent=True)
        self._set_focus(0)

    def _on_cancel(self) -> None:
        """Retorna para o menu principal."""
        from .menu import MenuScene

        self.app.change_scene(MenuScene(self.app))
