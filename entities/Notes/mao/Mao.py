from ..Note import Note
import pathlib
import pygame

class Mao(Note):
    def __init__(self, spawn_time: float, hit_time: float):
        super().__init__(spawn_time, hit_time, "m")

    @staticmethod
    def note_sound(self) -> None:
        """Reproduz mao.wav desta pasta."""
        folder = pathlib.Path(__file__).parent
        wav_path = folder / "mao.wav"
        if not wav_path.exists():
            print("mao.note_sound: arquivo mao.wav não encontrado.")
            return
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            sound = pygame.mixer.Sound(str(wav_path))
            sound.play()
        except pygame.error as e:
            print(f"mao.note_sound: erro ao reproduzir mao.wav: {e}")