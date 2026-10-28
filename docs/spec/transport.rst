Transport contract
==================

A transport implements the ``Transport`` abstract class:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Member
     - Requirement
   * - ``mtu`` (property)
     - Best-effort maximum frame size in bytes. Larger frames may be refused
       before sending.
   * - ``start()`` / ``stop()``
     - Bring the transport up and down. The protocol does not call these;
       the application owns the transport lifecycle.
   * - ``send(dest, frame)``
     - Send one frame to ``"peer:<id>"`` (exactly that peer) or
       ``"broadcast:*"`` (all reachable peers). Must not block for long.
   * - ``on_receive(cb)``
     - Register ``cb(source, frame)``. It is called once per received frame,
       with ``source`` in the form ``"peer:<id>"``.

Transports must:

* preserve frame boundaries, delivering each frame whole and unmodified;
* map peer IDs used in ``destid`` / ``sourceid`` to their own addressing.

Transports need not guarantee ordering or delivery. The protocol does not
depend on either.

A transport with its own typed wire format, such as DDS, can carry the
envelope as fields instead of a JSON frame. Construct its ``Protocol`` with
``pack_frames=False``: ``send`` then receives the ``Message`` itself, and the
transport passes a ``Message`` to the ``on_receive`` callback. It must deliver
every envelope field, the payload, and the binary attachment unchanged. The
``mtu`` guard still measures the message as ``pack_frame`` would encode it.
