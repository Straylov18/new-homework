from abc import ABC

from src.game.room import GameRoom


class RoomContainer(ABC):
    _game_room: GameRoom | None = None

    @classmethod
    def get_room(cls) -> GameRoom:
        if cls._game_room is None:
            cls._game_room = GameRoom()
        return cls._game_room
