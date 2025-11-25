"""Cena de seleção de músicas do jogo."""

import pygame
import pathlib

from .base import BaseScene
from entities.Music import Music
from utils.buttons import Button, ButtonTheme
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, SCREEN_WIDTH, SCREEN_HEIGHT

class MusicSelectScene(BaseScene):
    """Cena com lista das músicas disponíveis e pré-visualização da música selecionada"""
    def __init__(self, app) -> None:
        """Configura fontes, tema e layout inicial do menu."""
        super().__init__()
        self.app = app
        self.title_font = pygame.font.Font(None, 82)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 42)
        self.theme = ButtonTheme(
            background=(42, 52, 71),
            background_hover=(70, 92, 141),
            border=(20, 28, 43),
            text=COLOR_TEXT,
        )
        self.buttons = self._build_buttons()
        self._title_pos = (SCREEN_WIDTH + 60, SCREEN_HEIGHT + 60)
        self._subtitle_pos = (SCREEN_WIDTH + 120, SCREEN_HEIGHT + 60)
        self._layout_size = (0, 0)
        self._apply_layout(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Músicas válidas
        self.songs = self._load_songs()
        self.selected_index = 0

    def _build_buttons(self) -> list[Button]:
        """Cria os botões com seus respectivos callbacks."""
        labels_callbacks = [
            ("Voltar", self._on_home_selected),
            ("Adicionar Música", self._on_add_music_selected),
            ("Tela Cheia", self._on_toggle_fullscreen),
        ]
        return [
            Button(pygame.Rect(0, 0, 0, 0), label, self.button_font, callback, self.theme)
            for (label, callback) in labels_callbacks
        ]
    
    def _apply_layout(self, width: int, height: int) -> None:
        """Posiciona os botões conforme o tamanho da tela."""
        button_width = min(250, int(width * 0.3))
        button_height = 60
        spacing = 20
        
        # Posiciona botões no canto inferior direito
        start_x = width - button_width - 40
        start_y = height - (len(self.buttons) * (button_height + spacing)) - 40
        
        for index, button in enumerate(self.buttons):
            y = start_y + index * (button_height + spacing)
            button.rect = pygame.Rect(start_x, y, button_width, button_height)
        
        self._layout_size = (width, height)
    
    def _load_songs(self) -> list[dict]:
        """Escaneia a pasta 'musics' por músicas válidas."""
        print("Carregando músicas...")
        songs_dir = pathlib.Path("musics")
        song_list = []

        # Itera pelas pastas em 'musics'
        for song_folder in songs_dir.iterdir():
            # Valida existência dos arquivos necessários
            if song_folder.is_dir():
                csv_file = list(song_folder.glob("*.csv"))
                mp3_file = list(song_folder.glob("*.mp3"))

                # Se ambos existirem e só um de cada, a música é válida
                if len(csv_file) == 1 and len(mp3_file) == 1:
                    song_data = Music(song_folder.name, csv_file[0], mp3_file[0])
                    song_list.append(song_data) # Adiciona à lista de músicas válidas
                    print(f"Música encontrada: {song_data.title}")
                else:
                    print(f"Pasta '{song_folder.name}' ignorada: requer 1 CSV e 1 MP3")

        if len(song_list) == 0:
            print("Nenhuma música válida encontrada!")

        # Retorna músicas válidas
        return song_list

    def _play_preview(self) -> None:
        """Toca trecho da música selecionada"""
        if not self.songs:
            return
        
        try:
            song = self.songs[self.selected_index]
            pygame.mixer.music.load(song.mp3_path)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(loops = 0, start = 30.0, fade_ms = 500)
        
        except pygame.error as e:
            print(f"Erro ao carregar o preview: {e}")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Lida com a seleção (teclas cima/baixo) e confirmação (Enter)."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.songs:
                    self.selected_index = (self.selected_index + 1) % len(self.songs)
                    self._play_preview()
            
            elif event.key == pygame.K_UP:
                if self.songs:
                    self.selected_index = (self.selected_index - 1) % len(self.songs)
                    self._play_preview()
            
            elif event.key == pygame.K_RETURN: # Tecla Enter
                self._on_song_selected()

            elif event.key == pygame.K_ESCAPE: # Voltar para o menu
                self._on_home_selected()


    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza layout da cena"""
        self.draw_background(surface, COLOR_BACKGROUND)
        width, height = surface.get_size()

        # Preview (esquerda)
        preview_panel_rect = pygame.Rect(0, 0, width // 2, height)
        preview_surface = surface.subsurface(preview_panel_rect)
        self.render_preview(preview_surface)
        # pygame.draw.rect(surface, (255, 0, 0), preview_panel_rect, 3)

        # Músicas (direita)
        music_selection_rect = pygame.Rect(width // 2, 0, width // 2, height)
        music_surface = surface.subsurface(music_selection_rect)
        self.render_music_list(music_surface)
        # pygame.draw.rect(surface, (0, 0, 255), music_selection_rect, 3)

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Quebra o texto em múltiplas linhas se exceder a largura máxima."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]

    def render_preview(self, surface: pygame.Surface) -> None:
        """Renderiza pré-visualização da música selecionada"""
        if not self.songs:
            no_song_font = pygame.font.Font(None, int(self.title_font.get_height() * 0.75))
            txt = no_song_font.render("Nenhuma música", True, COLOR_TEXT_MUTED)
            surface.blit(txt, txt.get_rect(center=surface.get_rect().center))
            return
        
        song = self.songs[self.selected_index]

        # Quebra o título se necessário
        max_width = surface.get_width() * 0.9  # 90% da largura
        lines = self._wrap_text(song.title, self.title_font, max_width)
        
        # Calcula altura total do texto
        line_height = self.title_font.get_linesize()
        total_height = len(lines) * line_height
        start_y = (surface.get_height() - total_height) // 2
        
        # Renderiza cada linha centralizada
        for i, line in enumerate(lines):
            title_txt = self.title_font.render(line, True, COLOR_PRIMARY)
            y_pos = start_y + i * line_height
            x_pos = (surface.get_width() - title_txt.get_width()) // 2
            surface.blit(title_txt, (x_pos, y_pos))

    def render_music_list(self, surface: pygame.Surface) -> None:
        """Renderiza painel de seleção das músicas"""
        line_height = 50
        total_height = len(self.songs) * line_height
        start_y = (surface.get_height() - total_height) // 2
        max_width = surface.get_width() * 0.85  # 85% da largura

        for index, song in enumerate(self.songs):
            is_selected = (index == self.selected_index)
            color = COLOR_PRIMARY if is_selected else COLOR_TEXT
            prefix = "> " if is_selected else "  "
            
            # Quebra o texto se necessário
            full_text = prefix + song.title
            lines = self._wrap_text(full_text, self.button_font, max_width)
            
            # Renderiza apenas a primeira linha
            text = lines[0] if lines else full_text
            if len(lines) > 1:
                text += "..."  # Indica que há mais texto
            
            txt_render = self.button_font.render(text, True, color)
            pos_x = surface.get_width() * 0.1
            pos_y = start_y + index * line_height
            surface.blit(txt_render, (pos_x, pos_y))

    def _on_song_selected(self) -> None:
        """Ao pressionar ENTER ou clicar na música, direciona para a cena de jogo"""
        if not self.songs:
            return
        
        pygame.mixer.music.stop()
        song = self.songs[self.selected_index]
        
        from .gameplay import GameplayScene # importação tardia evitando importação circular
        self.app.change_scene(GameplayScene(self.app, song))  # Passa dados da música

    def _on_home_selected(self) -> None:
        """Volta para o menu principal"""
        pygame.mixer.music.stop()
        from .menu import MenuScene
        self.app.change_scene(MenuScene(self.app))

    def _on_add_music_selected(self) -> None:
        """Direciona para a tela de adição de músicas"""
        print("TODO: fazer tela de adição de músicas")

    def _on_toggle_fullscreen(self) -> None:
        """Solicita ao controlador a alternância de modo de tela."""
        self.app.toggle_fullscreen()