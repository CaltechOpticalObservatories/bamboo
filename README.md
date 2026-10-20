# bamboo

bamboo is a messaging protocol for observatory operations. Instruments,
hardware daemons, core services, GUIs and automation scripts use it to talk
to each other with one shared vocabulary:

- **Request / response**: call a named handler on another peer and get a result back.
- **Configuration**: push settings to a peer and know they arrived.
- **Publish / subscribe**: publish telemetry and events on topics.
- **Discovery**: peers announce the handlers they serve and the topics they follow.
- **Binary attachments**: send raw bytes, such as a compressed detector frame, alongside a message's JSON.

bamboo sits above the transport. It produces and consumes plain byte frames,
so it can run over Zyre, ZeroMQ, a message broker, or anything else that can
move a frame.

📖 **Documentation:** https://caltechopticalobservatories.github.io/bamboo/

## Install

Requires Python 3.11 or later.

```bash
git clone git@github.com:CaltechOpticalObservatories/bamboo.git
cd bamboo
pip install -e .
```

## Example

bamboo needs a transport to move frames between peers. This one delivers them
within a single process, which is enough to try the protocol:

```python
from bamboo import Protocol, Transport


class LocalTransport(Transport):
    """Delivers frames between peers in the same process."""

    peers = {}
    mtu = 1_000_000

    def __init__(self, peer_id):
        self.peer_id = peer_id
        LocalTransport.peers[peer_id] = self

    def start(self): pass
    def stop(self): pass

    def on_receive(self, cb):
        self._cb = cb

    def send(self, dest, frame):
        kind, _, target = dest.partition(":")
        for pid, peer in LocalTransport.peers.items():
            if pid != self.peer_id and (kind == "broadcast" or pid == target):
                peer._cb(f"peer:{self.peer_id}", frame)


# A peer that serves the "camera.capture" key
camera = Protocol(LocalTransport("camera-1"), self_id="camera-1")
camera.serve("camera.capture",
             lambda payload, ctx: {"ok": True, "data": {"image_id": 42}})

# A peer that calls it
client = Protocol(LocalTransport("controller"), self_id="controller")
print(client.request_peer("camera-1", "camera.capture", {"exposure_ms": 20}))
# {'status': 'delivered', 'transid': '...', 'resp': {'ok': True, 'data': {'image_id': 42}}}
```

The camera acknowledges the request as soon as it accepts it, runs the
handler, and sends back a response with the same transaction ID. To connect
real peers, implement the
[transport contract](https://caltechopticalobservatories.github.io/bamboo/spec/transport.html)
for your network.

## Repository layout

```
protocol/   the bamboo Python package (installed as `bamboo`)
docs/       Sphinx documentation: design and protocol specification
```

## Building the docs

```bash
pip install -e '.[docs]'
sphinx-build -a -b html docs docs/_build/html
open docs/_build/html/index.html
```

The docs are built on every pull request and published to GitHub Pages when
changes land on `main`.
