Why bamboo
==========

bamboo is a single messaging layer for observatory operations. Instruments,
hardware daemons, core services, GUIs and automation scripts all speak the
same protocol, whether they talk to each other directly or through a broker.

What observatory systems need
-----------------------------

Every subsystem needs the same things, and they should be solved once rather
than reimplemented for each subsystem:

* message framing and meaning;
* logical addressing and routing;
* configurable reliability and ordering;
* state recovery and observability.

Why a shared protocol
---------------------

Different subsystems need different communication models: peer-to-peer or
brokered, publish/subscribe or request/reply. A protocol that sits above the
transport lets these models coexist, while applications see one consistent
interface and behavior.

A reusable protocol also means teams stop solving the same integration
problems for every new instrument. Systems last longer, cost less to
maintain, and new instruments and services can be added without
re-architecting how everything communicates.

Design goals
------------

**Transport agnostic**
   Message structure and meaning are independent of the transport, so the
   same protocol runs over ZeroMQ, Zyre, raw TCP, a message broker, or
   anything else that can move a frame.

**Hybrid topology**
   Both peer-to-peer and brokered deployments are supported, so each
   subsystem can use the pattern that suits it. See :doc:`topologies`.

**Performance**
   Low latency for commands and high throughput for telemetry.

**Observability**
   Every message carries a transaction ID that is kept end to end, so one
   operation can be traced through the logs of every peer it touched.

**Robustness**
   Message integrity, graceful failure handling, and recovery from partial
   outages.
