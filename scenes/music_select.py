"""Cena de seleção de músicas do jogo."""

import pygame
import pathlib

from .base import BaseScene
from utils.buttons import Button, ButtonTheme
from utils.constants import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_MUTED, SCREEN_WIDTH, SCREEN_HEIGHT

class MusicSelectScene(BaseScene):
    """Cena com lista das músicas disponíveis e pré-visualização da música selecionada"""
    def __init__(self, app) -> None:
        """Configura fontes, tema e layout inicial do menu."""
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
                song_data = {
                    "title": song_folder.name,
                    "csv_path": csv_file[0],
                    "mp3_path": mp3_file[0]
                }
            else:
                print(f"A música {song_folder.name} é inválida (verifique os arquivos csv e mp3!)")

            # Adiciona à lista de músicas válidas
            song_list.append(song_data)
            print(f"Música encontrada: {song_data['title']}")

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
            pygame.mixer.music.load(song['mp3_path'])
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
                self.app.set_scene(self.app.menu_scene) # (Veja Etapa 2)


    def update(self, dt: float) -> None:
        """Verifica se a música de preview terminou."""
        # Opcional: se a música de preview acabar, pare-a.
        if not pygame.mixer.music.get_busy():
            pass # Você pode reiniciar o preview se quiser

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza layout da cena"""
        surface.fill(COLOR_BACKGROUND)
        width, height = surface.get_size()

        # Preview (esquerda)
        preview_panel_rect = pygame.Rect(0, 0, width // 2, height)
        self.render_preview(surface.subsurface(preview_panel_rect))

        # Músicas (direita)
        music_selection_rect = pygame.Rect(width // 2, 0, width // 2, height)
        self.render_music_list(surface.subsurface(music_selection_rect))

    def render_preview(self, surface: pygame.Surface) -> None:
        """Renderiza pré-visualização da música selecionada"""
        if not self.songs:
            txt = self.title_font.render("Nenhuma música", True, COLOR_TEXT_MUTED)
            surface.blit(txt, txt.get_rect(center=surface.get_rect().center))
            return
        
        song = self.songs[self.selected_index]

        # Titulo
        title_txt = self.title_font.render(song["title"], True, COLOR_PRIMARY)
        title_pos = (surface.get_width() // 4, surface.get_height() * 0.3)
        surface.blit(title_txt, title_txt.get_rect(center=title_pos))

    def render_music_list(self, surface: pygame.Surface) -> None:
        """Renderiza painel de seleção das músicas"""
        start_y = 100 # Posição Y inicial da lista
        line_height = 50 # Espaço entre cada música

        for index, song in enumerate(self.songs):
            is_selected = (index == self.selected_index)

            color = COLOR_PRIMARY if is_selected else COLOR_TEXT

            # Adiciona "> " no título da música selecionada
            prefix = "> " if is_selected else "  "
            text = prefix + song["title"]

            txt_render = self.button_font.render(text, True, color)

            # Centraliza o texto
            pos_x = surface.get_width() * 0.1
            pos_y = start_y + index * line_height

            surface.blit(txt_render, (pos_x, pos_y))

    def _on_song_selected(self) -> None:
        """Ao pressionar ENTER ou clicar na música, direciona para a cena de jogo"""
        if not self.songs:
            return
        
        pygame.mixer.music.stop() # Para preview

        song = self.songs[self.selected_index]
        # TODO: fazer direcionamento para a tela de jogo

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