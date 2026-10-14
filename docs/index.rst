bamboo
======

bamboo is a messaging protocol for observatory operations. Instruments,
hardware daemons, core services, GUIs and automation scripts all use it to
talk to each other. Every peer gets the same simple vocabulary: ask another
peer to do something, push it new configuration, or publish telemetry to
whoever is interested. None of this ties you to a particular network library.

bamboo defines discovery, routing and delivery rules once, above the
transport, so new instruments and services plug into the same system instead
of each solving those problems on its own. The full motivation is in
:doc:`design/why`.

What bamboo gives you
---------------------

**Request / response.** Call a named handler on another peer and get a result
back: ``request_peer("camera-1", "camera.capture", {...})``.

**Configuration pushes.** Send settings to a peer with ``CONFIG`` and know
they arrived.

**Publish / subscribe.** Publish events on a topic. Subscribers receive them
directly, and if no subscribers are known yet, the event is broadcast.

**Discovery.** Peers announce the handlers (*keys*) they serve and the topics
they subscribe to, so each peer knows who can do what.

**Binary payloads.** Any message can carry a raw binary attachment alongside
its JSON body, for example a compressed image chunk.

**Pluggable transports.** The protocol produces and consumes plain byte
frames, so any message-oriented transport can carry it. Zyre is the first
target.

How it works
------------

Every message is a small JSON *envelope* with a type, a transaction ID, a
key, a payload, and source and destination peer IDs. A message sent directly
to one peer is acknowledged as soon as that peer accepts it. A request is then
answered with a response that carries the same transaction ID. Broadcasts and
events are fire-and-forget.

A peer only accepts direct requests for keys it has registered. Requests for
anything else are dropped silently, so a typo or a missing service shows up as
a timeout rather than an error reply.

.. mermaid::

   sequenceDiagram
       participant A as controller
       participant B as camera-1
       A->>B: REQ camera.capture (transid T)
       Note right of B: serves camera.capture?
       B-->>A: ACK (T)
       Note right of B: run handler
       B-->>A: RESP (T, ok, data)

Quick look
----------

A peer that serves a key:

.. code-block:: python

   from bamboo import Protocol

   camera = Protocol(transport, self_id="camera-1")

   def capture(payload, ctx):
       image_id = take_exposure(payload["exposure_ms"])
       return {"ok": True, "data": {"image_id": image_id}}

   camera.serve("camera.capture", capture)

A peer that calls it:

.. code-block:: python

   from bamboo import Protocol

   client = Protocol(transport, self_id="controller")
   result = client.request_peer("camera-1", "camera.capture", {"exposure_ms": 20})

   # {"status": "delivered", "transid": "...",
   #  "resp": {"ok": True, "data": {"image_id": ...}}}

Here ``transport`` is any implementation of :doc:`the transport contract
<spec/transport>`, and ``take_exposure`` stands in for your own code.

Where to go next
----------------

* :doc:`design/why`: the problem bamboo solves and its design goals.
* :doc:`design/architecture` and :doc:`design/topologies`: where bamboo sits
  in the observatory software stack, and peer-to-peer vs. brokered
  deployments.
* :doc:`spec/index`: start here for the protocol overview and terminology.
* :doc:`spec/wire-format` and :doc:`spec/message-types`: what goes over the
  wire.
* :doc:`spec/delivery`: ACKs, responses, timeouts and what a receiver does
  with each message.
* :doc:`spec/transport`: what you need to implement to add a new transport.

.. toctree::
   :hidden:
   :caption: Design

   design/why
   design/architecture
   design/topologies

.. toctree::
   :hidden:
   :caption: Protocol specification

   spec/index
   spec/wire-format
   spec/message-types
   spec/delivery
   spec/keys-discovery
   spec/pubsub
   spec/transport
   spec/reference

.. toctree::
   :hidden:
   :caption: Reference

   glossary
