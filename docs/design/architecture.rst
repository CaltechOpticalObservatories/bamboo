Architecture
============

Observatory software is organized as a stack of layers, and each layer can
evolve independently. bamboo is the **protocol** layer.

.. mermaid::

   flowchart TB
       app["<b>Application</b><br/>GUIs, CLIs,<br/>automation scripts"]
       daemons["<b>Daemons</b><br/>hardware abstraction,<br/>orchestration,<br/>core services"]
       protocol["<b>Protocol: bamboo</b><br/>framing, routing,<br/>message types"]
       transport["<b>Wire transport</b><br/>ZeroMQ, Zyre, MQTT,<br/>UDP, sockets"]
       app --> daemons --> protocol --> transport

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Layer
     - Responsibility
   * - Application
     - GUIs, command-line tools, and high-level automation scripts.
   * - Daemons
     - Hardware abstraction, orchestration, and core services.
   * - Protocol
     - The rules for framing, routing and message types. This is bamboo.
   * - Wire transport
     - Physical delivery of bytes, for example ZeroMQ, MQTT, UDP or sockets.

Protocol vs. transport
----------------------

The split between these two layers is what lets bamboo run anywhere.

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Protocol: *what is being said*
     - Transport: *how the bytes move*
   * - Message envelope: fields, types, metadata
     - Connection setup and teardown
   * - Serialization: JSON, binary framing
     - Delivery mechanics: brokers, peer sockets, multicast
   * - Message meaning: REQ/RESP, PUB/SUB, ACK, CONFIG, HELLO
     - Buffering and flow control
   * - Routing: source, destination, broadcast, keys
     - Chunking messages on the wire
   * - Delivery guarantees
     - Network topology: client/server, brokered, mesh
   * - Lifecycle: HELLO, heartbeats, health
     - Transport-level guarantees, e.g. TCP ordering

In code, the protocol layer is the ``bamboo`` package, and each transport is
an implementation of the ``Transport`` class (see :doc:`/spec/transport`).

.. _core-services:

Core services
-------------

A *core service* is a long-lived daemon that provides observatory-wide
infrastructure rather than serving a single instrument. Other daemons and
applications depend on it, so it is part of the platform and must be present
in every deployment. A discovery registry or a message broker is an example.
