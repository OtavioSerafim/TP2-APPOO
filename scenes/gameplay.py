import pygame
import csv

from .base import BaseScene
from utils.constants import COLOR_BACKGROUND, SCREEN_WIDTH, SCREEN_HEIGHT

COLOR_YELLOW_BACKGROUND = (228, 177, 39)
COLOR_PINK_NOTE = (230, 52, 120)
COLOR_BLUE_NOTE = (77, 87, 228)
COLOR_GREEN_NOTE = (77, 228, 127)
COLOR_YELLOW_NOTE = (224, 208, 77)


class GameplayScene(BaseScene):
    """Cena onde ocorre toda a jogabilidade"""
    def __init__(self, app, song_data: dict):
        self.app = app
        self.song_data = song_data
        self.note_radius = 160 // 3
        self.note_speed = 300
        self.hit_area_x = 300
        self.notes = []  # Notas ativas na tela
        self.note_queue = []  # Notas aguardando spawn (do CSV)
        self.start_time = None  # Timestamp do início da música

        # Inicializa posições da lane
        height = self.app.screen.get_height()
        self.lane_bottom = height // 2
        self.lane_top = self.lane_bottom - 200
        self.lane_rect = pygame.Rect(0, self.lane_top, self.app.screen.get_width(), 200)

        # Calcula tempo para a nota chegar à hit_area
        width = self.app.screen.get_width()
        spawn_x = width + self.note_radius
        distance = spawn_x - self.hit_area_x
        self.anticipation_time = distance / self.note_speed  # Em segundos
        
        self._load_beatmap()
        self._start_music()

    def _load_beatmap(self) -> None:
        """Carrega timestamps das notas do arquivo CSV"""
        try:
            with open(self.song_data['csv_path'], 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    hit_time = float(row.get('time', 0))  # Tempo quando nota deve estar na hit_area
                    note_type = row.get('note', 'g').lower()
                    
                    if note_type not in ['g', 'a', 'm', 'f']:
                        print(f"Tipo de nota inválido '{note_type}', usando 'g'")
                        note_type = 'g'
                        
                    spawn_time = hit_time
                    
                    self.note_queue.append({
                        'spawn_time': spawn_time,
                        'hit_time': hit_time,
                        'note_type': note_type,
                        'spawned': False
                    })
            
            self.note_queue.sort(key=lambda n: n['spawn_time'])
            print(f"Carregadas {len(self.note_queue)} notas do beatmap")
            print(f"Tempo de antecipação: {self.anticipation_time:.2f}s")
            
            # Debug: mostra as primeiras notas
            for i, note in enumerate(self.note_queue[:5]):
                print(f"Nota {i+1}: spawn={note['spawn_time']:.2f}s, tipo={note['note_type']}")
        
        except Exception as e:
            print(f"Erro ao carregar beatmap: {e}")
            self.note_queue = []

    def _start_music(self) -> None:
        """Inicia a reprodução da música após o tempo de antecipação"""
        try:
            pygame.mixer.music.load(self.song_data['mp3_path'])
            pygame.mixer.music.set_volume(0.5)
            
            # Marca o tempo inicial ANTES de tocar
            self.start_time = pygame.time.get_ticks()
            
            # Agenda a música para tocar após o tempo de antecipação
            delay_ms = int(self.anticipation_time * 1000)  # Converte para milissegundos
            pygame.time.set_timer(pygame.USEREVENT + 1, delay_ms, 1)  # Timer único
            
            print(f"Música iniciará em {self.anticipation_time:.2f}s")
        except pygame.error as e:
            print(f"Erro ao carregar música: {e}")

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza layout da cena"""
        surface.fill(COLOR_YELLOW_BACKGROUND)
        self.render_lane(surface)
        self.render_hit_area(surface)
        self.render_notes(surface)

    def render_lane(self, surface: pygame.Surface) -> None:
        """Desenha a lane em que percorrem as notas"""
        width = surface.get_width()
        self.lane_rect = pygame.Rect(0, self.lane_top, width, 200)

        pygame.draw.rect(surface, COLOR_BACKGROUND, self.lane_rect)
        border_thickness = 2
        pygame.draw.line(surface, (255, 255, 255), (0, self.lane_top), (width - 1, self.lane_top), border_thickness)
        pygame.draw.line(surface, (255, 255, 255), (0, self.lane_bottom - 1), (width - 1, self.lane_bottom - 1), border_thickness)

    def render_hit_area(self, surface: pygame.Surface) -> None:
        """Desenha a área de acerto das notas"""
        hit_radius = 80
        hit_center_y = self.lane_bottom - 100

        hit_surf = pygame.Surface((hit_radius * 2, hit_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(hit_surf, (255, 255, 255, 40), (hit_radius, hit_radius), hit_radius)
        pygame.draw.circle(hit_surf, (255, 255, 255, 160), (hit_radius, hit_radius), 2 * hit_radius // 3)
        surface.blit(hit_surf, (self.hit_area_x - hit_radius, hit_center_y - hit_radius))
    
    def render_note(self, surface: pygame.Surface, note_center_x: int, note_center_y: int, note_type: str) -> None:
        """Desenha uma nota com base no seu tipo"""
        if note_type == "g": note_color = COLOR_PINK_NOTE
        elif note_type == "a": note_color = COLOR_BLUE_NOTE
        elif note_type == "m": note_color = COLOR_YELLOW_NOTE
        elif note_type == "f": note_color = COLOR_GREEN_NOTE

        note_surf = pygame.Surface((self.note_radius * 2, self.note_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(note_surf, note_color, (self.note_radius, self.note_radius), self.note_radius)
        surface.blit(note_surf, (note_center_x - self.note_radius, note_center_y - self.note_radius))

    def render_notes(self, surface: pygame.Surface) -> None:
        """Renderiza todas as notas ativas"""
        for note in self.notes:
            self.render_note(surface, int(note["x"]), note["y"], note["type"])

    def spawn_note(self, note_type: str) -> None:
        """Cria uma nova nota fora da tela à direita"""
        width = self.app.screen.get_width()
        new_note = {
            "x": width + self.note_radius,
            "y": self.lane_bottom - 100,
            "type": note_type
        }
        self.notes.append(new_note)

    def handle_event(self, event: pygame.event.Event) -> None:
        # Timer para iniciar a música
        if event.type == pygame.USEREVENT + 1:
            pygame.mixer.music.play()
            print("Música iniciada!")
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.music.stop()
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancela timer
            from .music_select import MusicSelectScene
            self.app.change_scene(MusicSelectScene(self.app))

    def update(self, dt: float) -> None:
        """Atualiza posição das notas e spawna baseado no timer real"""
        if self.start_time is None:
            return
        
        # Calcula tempo decorrido usando pygame.time.get_ticks()
        current_time = pygame.time.get_ticks()
        music_time = (current_time - self.start_time) / 1000.0  # Converte ms para segundos
        
        # Spawna notas do beatmap no momento certo
        for note_data in self.note_queue:
            if not note_data['spawned'] and music_time >= note_data['spawn_time']:
                self.spawn_note(note_data['note_type'])  # Passa o tipo da nota
                note_data['spawned'] = True
        
        # Move todas as notas
        for note in self.notes:
            note["x"] -= self.note_speed * dt
        
        # Remove notas que passaram da área de acerto
        self.notes = [note for note in self.notes if note["x"] >= 250]