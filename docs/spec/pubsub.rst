Publish / subscribe
===================

Subscribing
-----------

``Protocol.listen(topic, handler)`` registers a local event handler and, if
the topic is new, broadcasts a ``SUBSCRIBE`` with ``add=[topic]``.
``Protocol.subscribe_topics(add, remove)`` broadcasts a ``SUBSCRIBE`` only if
the local subscription set actually changed. Peers also learn subscriptions
from the ``subs`` field of ``HELLO``.

.. mermaid::

   sequenceDiagram
       participant S as subscriber
       participant P as publisher
       Note over S: listen("telemetry.temp", handler)
       S->>P: SUBSCRIBE add telemetry.temp (broadcast)
       Note over P: record subscriber for telemetry.temp
       P->>S: PUB telemetry.temp (direct)
       Note over S: handler runs

Publishing
----------

``Protocol.publish(topic, payload)`` chooses one of two delivery modes:

.. mermaid::

   flowchart LR
       P["publish(topic, payload)"] --> Q{known subscribers<br/>for topic?}
       Q -- yes --> F["direct PUB to each subscriber<br/>(no waiting)"]
       Q -- no --> B[broadcast one PUB]

* **Fan-out.** If any peers are known to subscribe to ``topic``, it sends one
  direct ``PUB`` to each of them, without waiting.
* **Broadcast fallback.** Otherwise, it broadcasts a single ``PUB``.

Receivers deliver a ``PUB`` to the handler registered for its topic, if any.
Exceptions in event handlers are swallowed.
