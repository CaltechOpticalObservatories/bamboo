from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable

DestStr = str   # "peer:<uuid>" or "group:<name>"
SrcStr  = str   # "peer:<uuid>"

class Transport(ABC):

    # False: send() and on_receive callbacks carry Message objects, for
    # transports that encode the envelope in their own typed wire format
    pack_frames: bool = True

    @property
    @abstractmethod
    def mtu(self) -> int:
        """Best-effort max frame size in bytes."""
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send(self, dest: DestStr, frame: bytes) -> None:
        """Send one frame to a destination string."""
        raise NotImplementedError

    @abstractmethod
    def on_receive(self, cb: Callable[[SrcStr, bytes], None]) -> None:
        raise NotImplementedError
