Protocol overview
=================

:Protocol version: 1
:Status: Draft
:Reference implementation: ``bamboo`` Python package (``protocol/``)

This specification describes the bamboo messaging protocol as the reference
implementation behaves today.

Design goals
------------

* **Transport independence.** The protocol layer only produces and consumes
  opaque byte frames. Any message-oriented transport can carry them.
* **Simple delivery.** Messages are sent once. Direct messages are
  acknowledged, there are no retries, and the application handles duplicate
  detection.
* **Key-gated services.** A peer only accepts direct requests for *keys* it
  advertises. Anything else is dropped silently.
* **Publish / subscribe.** Peers publish events on topics, and subscribers
  receive them directly or by broadcast.

Layers
------

.. mermaid::

   flowchart TB
       app["<b>Application</b><br/>handlers and listeners"]
       proto["<b>Protocol runtime</b><br/>ACK/RESP matching<br/>key gating<br/>subscriptions<br/>discovery"]
       wire["<b>Framing</b><br/>JSON envelope<br/>+ optional binary"]
       transport["<b>Transport</b><br/>Zyre, ...<br/>peer:ID<br/>broadcast:*"]
       app <--> proto <--> wire <--> transport

Terminology
-----------

Peer
   A participant with a stable, unique identifier (``sourceid`` / ``destid``).

Direct message
   A message whose ``destid`` is set. It goes to exactly one peer.

Broadcast message
   A message whose ``destid`` is ``null``. It goes to every reachable peer.

Key
   A string naming a handler on a peer (for example ``"camera.capture"``).
   For ``PUB`` messages, the key holds the *topic*.

Capability (cap)
   A string advertising a feature a peer supports (for example ``"json"``).

Transaction ID (transid)
   An identifier that correlates a request with its ``ACK`` and ``RESP``.

Frame
   The serialized bytes of one message, as handed to the transport.

Specification pages
-------------------

.. list-table::
   :widths: 30 70

   * - :doc:`wire-format`
     - Frame layout and the envelope fields.
   * - :doc:`message-types`
     - Every message type and its payload.
   * - :doc:`delivery`
     - Addressing, ACKs, responses, timeouts and receiver rules.
   * - :doc:`keys-discovery`
     - Key registry, key gating and ``HELLO`` discovery.
   * - :doc:`pubsub`
     - Subscribing and publishing.
   * - :doc:`transport`
     - What a transport must implement.
   * - :doc:`reference`
     - Reserved names and versioning.
