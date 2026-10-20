Wire format
===========

Frame layout
------------

A frame is a UTF-8 JSON object (the *envelope*), optionally followed by a
binary attachment:

.. mermaid::

   flowchart LR
       H["<b>header</b><br/>UTF-8 JSON envelope<br/>compact, no whitespace"]
       S["<b>separator</b><br/>0x0A 0x0A"]
       B["<b>binary</b><br/>arbitrary bytes<br/>(optional)"]
       H --- S --- B

.. code-block:: text

   frame = header                       ; no binary attachment
         | header "\n\n" binary         ; with binary attachment

   header = UTF-8 JSON object, compact separators (no whitespace)
   binary = arbitrary bytes (e.g. a blosc-compressed chunk)

Receivers split the frame on the **first** occurrence of the two-byte sequence
``0x0A 0x0A`` (``"\n\n"``). Because the header is compact JSON, and JSON
escapes newlines inside strings, the header never contains that sequence, so
the binary part may contain arbitrary bytes, including ``"\n\n"``.

A frame with no separator has no binary attachment.

Envelope
--------

Every message carries all ten envelope fields. Optional fields are present
with the value ``null``; they are not omitted. Receivers treat a missing
``traceparent`` or ``tracestate`` as ``null``, so frames from older senders
still decode.

.. list-table::
   :header-rows: 1
   :widths: 12 14 74

   * - Field
     - JSON type
     - Meaning
   * - ``version``
     - integer
     - Protocol version. Currently ``1``. Responders copy the request's
       version into ``ACK`` and ``RESP``.
   * - ``type``
     - string
     - One of the :doc:`message types <message-types>`.
   * - ``transid``
     - string
     - Transaction ID. New messages get a random UUID4 as 32 lowercase hex
       characters (no dashes). ``ACK`` and ``RESP`` reuse the ``transid`` of
       the message they answer.
   * - ``key``
     - string | null
     - Handler name for ``REQ`` and ``CONFIG``; the topic for ``PUB``; a
       reserved name for system messages (see :doc:`reference`).
   * - ``payload``
     - object
     - JSON object. Its contents depend on ``type``. Defaults to ``{}``.
   * - ``time``
     - string
     - Sender's send time, ISO 8601 in UTC with a ``Z`` suffix, e.g.
       ``"2026-10-13T21:45:00.123456Z"``. Informational only.
   * - ``destid``
     - string | null
     - Destination peer ID. ``null`` means broadcast.
   * - ``sourceid``
     - string
     - Sender's peer ID.
   * - ``traceparent``
     - string | null
     - `W3C Trace Context <https://www.w3.org/TR/trace-context/>`_
       ``traceparent`` header, ``version-traceid-parentid-flags`` in
       lowercase hex, e.g.
       ``"00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"``.
       ``null`` means the message is not traced. ``ACK`` and ``RESP`` copy
       the request's value.
   * - ``tracestate``
     - string | null
     - W3C Trace Context ``tracestate`` header (vendor-specific key/value
       list). Only meaningful when ``traceparent`` is set. ``ACK`` and
       ``RESP`` copy the request's value.

Example
-------

A direct request with no binary attachment:

.. code-block:: json

   {
     "version": 1,
     "type": "REQ",
     "transid": "3f2b9c0e8d4a4e1f9b7c6a5d4e3f2a1b",
     "key": "camera.capture",
     "payload": {"exposure_ms": 20, "ttl_ms": 5000},
     "time": "2026-10-13T21:45:00.123456Z",
     "destid": "peer-b",
     "sourceid": "peer-a",
     "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
     "tracestate": null
   }

On the wire the header is serialized compactly
(``{"version":1,"type":"REQ",...}``).

Tracing
-------

``traceparent`` and ``tracestate`` use the names and formats of the W3C Trace
Context headers, so OpenTelemetry's default propagator can read and write them
directly. bamboo does not depend on OpenTelemetry and never creates trace
context itself; senders that want tracing set it explicitly:

.. code-block:: python

   from opentelemetry.propagate import inject, extract

   # sender, inside an active span
   carrier = {}
   inject(carrier)
   msg = (MessageBuilder(self_id)
          .req("camera.capture", {"exposure_ms": 20})
          .to("peer-b")
          .trace(carrier.get("traceparent"), carrier.get("tracestate"))
          .build())

   # receiver, inside a serve() callback
   def capture(payload, ctx):
       parent = extract({k: ctx[k] for k in ("traceparent", "tracestate") if ctx[k]})
       with tracer.start_as_current_span("camera.capture", context=parent):
           ...

The trace ID in ``traceparent`` is unrelated to ``transid``. ``transid``
matches one request to its ``ACK`` and ``RESP``; the trace ID can span many
transactions across many peers.
