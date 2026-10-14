Message types
=============

.. list-table::
   :header-rows: 1
   :widths: 13 15 18 12 42

   * - Type
     - Addressing
     - ``key``
     - ACKed?
     - Purpose
   * - `REQ`_
     - direct or broadcast
     - handler name (required if direct)
     - if direct
     - Invoke a handler; normally answered with ``RESP``.
   * - `RESP`_
     - direct
     - the request's key
     - no
     - Result of a ``REQ``.
   * - `ACK`_
     - direct
     - ``"sys.ack"``
     - no
     - Confirms a direct message was received and its key accepted.
   * - `CONFIG`_
     - direct
     - handler name (required)
     - yes
     - Push configuration to a peer. No ``RESP``.
   * - `HELLO`_
     - broadcast
     - ``"bamboo.hello"``
     - no
     - Advertise keys, capabilities and subscriptions.
   * - `PUB`_
     - direct or broadcast
     - topic (required if direct)
     - no
     - Publish an event on a topic.
   * - `SUBSCRIBE`_
     - usually broadcast
     - ``"bamboo.subscribe"``
     - if direct
     - Add or remove topic subscriptions.

REQ
---

Asks the receiver to run the handler registered for ``key``. The payload is
application-defined, with these reserved fields:

``ttl_ms`` (number, optional)
   How long the sender waits for the ``ACK``, in milliseconds. Defaults to
   8000. The receiver does not read this field.

``noresp`` / ``_noresp`` (boolean, optional)
   If true, the receiver runs the handler but sends no ``RESP``.

A broadcast ``REQ`` is not key-gated or ACKed, but any peer with a matching
handler runs it and, unless ``noresp`` is set, sends a direct ``RESP`` back to
the sender.

RESP
----

Carries the result of a ``REQ`` back to the requester. ``transid`` and
``key`` match the request, and ``destid`` is the requester. The payload is one
of:

.. code-block:: text

   {"ok": true,  "data": <handler return value>}
   {"ok": false, "error": "<message>"}

If the handler returns an object that already contains ``"ok"`` or
``"error"``, it is sent as-is instead of being wrapped. If the handler raises,
the receiver sends ``{"ok": false, "error": str(exception)}``.

ACK
---

Sent by the receiver as soon as a direct ``REQ``/``CONFIG`` passes key gating,
**before** the handler runs. An ``ACK`` therefore means "received and
accepted", not "processed successfully". Direct ``SUBSCRIBE`` messages are
also ACKed.

.. code-block:: json

   {"ack": "<transid>"}

CONFIG
------

Pushes configuration to the handler registered for ``key``. Only direct
``CONFIG`` messages are processed; receivers ignore broadcast ones. The
handler's return value and any exception it raises are discarded, and no
``RESP`` is sent. The sender treats the ``ACK`` as completion.

.. code-block:: json

   {"persist": true, "data": {"...": "..."}}

``persist`` tells the handler whether the configuration should survive a
restart. Defaults to ``true``.

HELLO
-----

A broadcast announcement of what a peer offers. Receivers update their key
registry and their record of the sender's subscriptions (see
:doc:`keys-discovery`).

.. code-block:: json

   {
     "caps":   ["json"],
     "keys":   ["camera.capture", "camera.config"],
     "subs":   ["telemetry.temp"],
     "rev":    7,
     "ts":     1760391900.12,
     "noresp": true
   }

``keys``, ``caps`` and ``subs`` are sorted and de-duplicated. ``rev`` is the
sender's advertisement revision and ``ts`` is a Unix timestamp in seconds.

PUB
---

An event on the topic named by ``key``. The payload is application-defined.
``PUB`` is never key-gated or ACKed. Receivers with a listener for the topic
deliver it, and everyone else drops it silently. See :doc:`pubsub`.

SUBSCRIBE
---------

Changes the sender's topic subscriptions:

.. code-block:: json

   {"add": ["telemetry.temp"], "remove": ["telemetry.humidity"], "noresp": true}

Receivers apply ``add`` and then ``remove`` to their record of the sender's
subscriptions.
