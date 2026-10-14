Reserved names and versioning
=============================

Reserved names
--------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Name
     - Use
   * - ``sys.ack``
     - ``key`` of ``ACK`` messages.
   * - ``bamboo.hello``
     - ``key`` of ``HELLO`` messages.
   * - ``bamboo.subscribe``
     - ``key`` of ``SUBSCRIBE`` messages.
   * - ``bamboo.discovery``, ``bamboo.keys``
     - Topics used by the older ``Discovery`` helper.

Applications should not register handlers or topics under the ``sys.`` or
``bamboo.`` prefixes.

Reserved payload fields
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Message type
     - Fields
   * - ``REQ``
     - ``ttl_ms``, ``noresp``, ``_noresp``
   * - ``RESP``
     - ``ok``, ``data``, ``error``
   * - ``CONFIG``
     - ``persist``, ``data``

Versioning
----------

The ``version`` field identifies the envelope and semantics described here
(version ``1``). It only ever increases. Responders echo the request's version
in ``ACK`` and ``RESP``. There is not yet any version negotiation, and
receivers do not reject unknown versions.
