"""Protocol with and without frame packing."""
from __future__ import annotations

import unittest
from typing import Any, Callable, Dict, List, Tuple

from bamboo import Message, MessageBuilder, Protocol, Transport


class LocalTransport(Transport):
    """Deliver whatever ``Protocol`` sends to peers in the same process."""

    mtu = 1_000_000

    def __init__(self, peers: Dict[str, "LocalTransport"], peer_id: str) -> None:
        self.peers = peers
        self.peer_id = peer_id
        self.sent: List[Tuple[str, Any]] = []
        self.callback: Callable[[str, Any], None] | None = None
        peers[peer_id] = self

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def on_receive(self, cb: Callable[[str, Any], None]) -> None:
        self.callback = cb

    def send(self, dest: str, frame: Any) -> None:
        self.sent.append((dest, frame))
        kind, _, target = dest.partition(":")
        for peer_id, peer in list(self.peers.items()):
            if peer_id != self.peer_id and (kind == "broadcast" or peer_id == target):
                peer.callback(f"peer:{self.peer_id}", frame)


def _pair(pack_frames: bool) -> Tuple[Protocol, Protocol, LocalTransport]:
    peers: dict = {}
    server = Protocol(LocalTransport(peers, "server"), "server", pack_frames=pack_frames)
    client_transport = LocalTransport(peers, "client")
    client = Protocol(client_transport, "client", pack_frames=pack_frames)
    server.serve("echo", lambda payload, _ctx: {"ok": True, "echo": payload})
    return server, client, client_transport


class PackFramesTests(unittest.TestCase):
    """The default sends bytes; ``pack_frames=False`` sends ``Message`` objects."""

    def test_request_round_trips_either_way(self) -> None:
        """Deliver a request and its response with and without packing."""
        for pack_frames in (True, False):
            _server, client, _transport = _pair(pack_frames)
            result = client.request_peer("server", "echo", {"x": 1}, timeout_s=1.0)
            self.assertEqual(result["resp"], {"ok": True, "echo": {"x": 1}}, pack_frames)

    def test_default_packs_bytes(self) -> None:
        """Hand the transport packed bytes by default."""
        _server, client, transport = _pair(pack_frames=True)
        client.publish("alerts", {})
        self.assertIsInstance(transport.sent[-1][1], bytes)

    def test_unpacked_hands_over_the_message(self) -> None:
        """Hand the transport the ``Message`` itself, binary part included."""
        server, client, transport = _pair(pack_frames=False)
        received: List[Message] = []
        server.listen("frames", received.append)
        msg = MessageBuilder("client").pub("frames", {"n": 1}).binary(b"\n\n\x00").to(None).build()
        client.send(msg)
        self.assertIs(transport.sent[-1][1], msg)
        self.assertEqual(received, [msg])


if __name__ == "__main__":
    unittest.main()
