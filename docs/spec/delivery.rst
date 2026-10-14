Delivery and processing
=======================

Addressing
----------

The protocol maps ``destid`` to a transport destination string:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ``destid``
     - Transport destination
   * - ``"<peer-id>"``
     - ``"peer:<peer-id>"``
   * - ``null``
     - ``"broadcast:*"``

Receivers do not check that ``destid`` matches their own ID. The transport is
trusted to deliver direct frames only to the addressed peer.

General rules
-------------

* Each message is sent **once**. The protocol never retries.
* Only direct ``REQ``, ``CONFIG`` and ``SUBSCRIBE`` messages are ACKed.
  Broadcasts, ``PUB``, ``HELLO``, ``ACK`` and ``RESP`` are never ACKed.
* ``ACK`` and ``RESP`` are matched to the outstanding request by ``transid``.
  An ``ACK`` or ``RESP`` with no matching request is dropped.
* Rejection is silent: a peer that does not serve a key sends nothing, and the
  requester sees a timeout.

Direct REQ
----------

.. mermaid::

   sequenceDiagram
       participant R as Requester
       participant P as Responder
       R->>P: REQ (transid T, key K)
       alt K is not a local key
           Note over P: drop silently
           Note over R: no ACK: timeout
       else K is a local key
           P-->>R: ACK (T)
           Note over P: run handler for K
           opt noresp not set
               P-->>R: RESP (T, ok or error)
           end
           Note over R: status delivered
       end

The requester waits up to *W* for the ``ACK``, where *W* is ``ttl_ms / 1000``
(``request``) or ``timeout_s`` (``request_peer``), defaulting to 8 s. After the
``ACK`` it waits up to *W* / 2 for the ``RESP``.

Direct CONFIG
-------------

.. mermaid::

   sequenceDiagram
       participant S as Sender
       participant R as Receiver
       S->>R: CONFIG (transid T, key K)
       alt K is not a local key
           Note over R: drop silently
           Note over S: status timeout
       else K is a local key
           R-->>S: ACK (T)
           Note over R: run handler for K, discard result
           Note over S: status delivered
       end

Request outcomes
----------------

The sender-side API (``Protocol.request`` / ``Protocol.request_peer``) reports
one of these outcomes:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - ``status``
     - Meaning
   * - ``sent``
     - Broadcast message handed to the transport. No ACK is expected.
   * - ``delivered``
     - ``ACK`` received. For ``REQ``, ``resp`` holds the ``RESP`` payload, or
       ``null`` if no ``RESP`` arrived within the response window.
   * - ``timeout``
     - No ``ACK`` within the wait window. Either the message was lost, or the
       peer is unreachable or does not serve the key.
   * - ``no_key``
     - Sender-side check: the local registry knows the destination does not
       advertise ``key``. Nothing was sent. (``request`` only.)
   * - ``too_large``
     - The frame is larger than the transport's ``mtu``. Nothing was sent.
       The result also contains ``mtu`` and ``size``. (``request_peer``
       only.)

Receiver processing rules
-------------------------

.. mermaid::

   flowchart TD
       F([frame received]) --> D[decode envelope]
       D --> T{type}
       T -- "ACK / RESP" --> W[hand to waiter for transid]
       T -- HELLO --> H["learn keys, caps, rev<br/>record subs"]
       T -- SUBSCRIBE --> S[apply add / remove] --> SD{direct?}
       SD -- yes --> SA[send ACK]
       T -- "REQ / CONFIG" --> G{direct?}
       G -- yes --> K{key served locally?}
       K -- no --> X([drop silently])
       K -- yes --> A[send ACK] --> DT{type}
       G -- no --> DT
       DT -- REQ --> RH[run handler] --> NR{noresp?}
       NR -- no --> RS[send RESP to sourceid]
       DT -- "CONFIG, direct" --> CH[run handler, discard result]
       DT -- "CONFIG, broadcast" --> I([ignore])
       T -- PUB --> P[deliver to topic listener]

For each incoming frame, a peer runs these steps in order:

1. **Decode.** Split the frame and parse the envelope.
2. **ACK.** Hand it to the waiter for ``transid``, if any. Stop.
3. **RESP.** Hand it to the waiter for ``transid``, if any. Stop.
4. **HELLO.** Learn the sender's keys, caps, rev and ts, and record its
   subscriptions if ``subs`` is not empty. Stop.
5. **SUBSCRIBE.** Apply ``add`` / ``remove`` to the sender's subscriptions.
   If direct, send an ``ACK``. Stop.
6. **Key gate.** For a direct ``REQ`` or ``CONFIG``: if ``key`` is missing or
   not a local key, drop the message silently. Otherwise send an ``ACK``.
7. **REQ.** Run the handler for ``key``, if any. Unless ``noresp`` /
   ``_noresp`` is set, send a direct ``RESP`` to ``sourceid``. Stop.
8. **CONFIG.** If direct, run the handler for ``key``, if any, and discard
   its result. Stop.
9. **PUB.** Deliver to the event handler for ``key``, if any. Stop.

Messages that match none of these steps are ignored.
