Keys and discovery
==================

Key registry
------------

Each peer keeps a key registry (``KeyRegistry``) with:

* **Local keys**: the handlers this peer serves. Registering a handler with
  ``Protocol.on`` or ``Protocol.serve`` adds its key.
* **Local caps**: advertised capabilities. Default ``{"json"}``.
* **Local revision**: a counter bumped each time local keys or caps change.
* **Remote state**, per peer: served keys, caps, last advertised revision,
  and last-seen time.

Key gating
----------

A direct ``REQ`` or ``CONFIG`` is accepted only if ``key`` is non-null **and**
is one of the receiver's local keys. Otherwise the receiver drops it without
replying. ``PUB``, ``SUBSCRIBE`` and broadcast messages are not key-gated.

Learning remote keys
--------------------

When a peer advertises its keys (through ``HELLO``, or manually through
``Protocol.learn_peer_keys``):

1. If the advertisement has a ``rev`` lower than the last ``rev`` recorded for
   that peer, it is stale. Only the last-seen time is updated.
2. Otherwise the peer's key set is replaced (the default) or merged, and its
   caps, rev and last-seen time are recorded.

Peers not seen for a configurable period (default 60 s) can be removed with
``KeyRegistry.prune``.

Discovery with HELLO
--------------------

Transports without built-in discovery rely on ``HELLO`` announcements. A peer
broadcasts ``HELLO`` (``Protocol.announce_hello``) to advertise its keys,
caps, subscriptions and revision.

.. mermaid::

   sequenceDiagram
       participant A as peer-a
       participant B as peer-b
       participant C as peer-c
       par broadcast
           A->>B: HELLO (keys, caps, subs, rev)
       and
           A->>C: HELLO (keys, caps, subs, rev)
       end
       Note over B,C: skip if rev is stale, else update key registry and subscriptions for peer-a
       B->>A: REQ camera.capture (direct, key now known)

Receivers:

1. update their key registry for the sender (using the revision rules above);
2. replace their record of the sender's subscriptions, if ``subs`` is not
   empty.

The protocol does not set a ``HELLO`` schedule. Applications should announce
at startup, whenever their keys or subscriptions change, and periodically
afterwards (for example every 5 s) so that new peers learn about them and
registry pruning works.

.. note::

   The package also ships an older ``Discovery`` helper. It periodically
   broadcasts ``REQ`` messages on the ``bamboo.discovery`` and ``bamboo.keys``
   topics instead of ``HELLO``. The ``Protocol`` runtime does not consume
   these, so new code should use ``HELLO``.
