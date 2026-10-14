Communication topologies
========================

bamboo is designed to run over two kinds of deployment:

* **Peer-to-peer (decentralized).** Components talk to each other directly.
  This favors low latency and low overhead.
* **Brokered (centralized).** A broker sits in the middle and handles routing
  and delivery. This favors reliability, scalability, simple operations, and
  simple endpoints. It suits devices that should stay minimal and rely on a
  central messaging service.

The topology matters in two places: how a peer **finds** its destination
(discovery), and how messages **travel** to it. Messages and application
behavior are the same in both topologies, so a subsystem can switch without
changing application code.

.. note::

   The diagrams on this page show the target design. bamboo 0.1 implements
   peer-to-peer discovery with ``HELLO`` broadcasts, and leaves address
   resolution to the transport. There is no registry or broker transport yet.

Peer-to-peer
------------

Peers find each other by broadcast or multicast, with or without a central
registry. This works well for resilient communication on a local subnet.

Discovery by broadcast
~~~~~~~~~~~~~~~~~~~~~~

.. mermaid::

   sequenceDiagram
       autonumber
       participant A as Peer A
       participant N as Broadcast network
       participant B as Peer B
       participant C as Peer C
       Note over A,C: Discovery phase
       A->>N: HELLO (broadcast): A id, reply address
       N-->>B: HELLO from A
       N-->>C: HELLO from A
       B->>A: HELLO: B id, address
       C->>A: HELLO: C id, address
       Note over A,C: Transaction phase (direct)
       A->>B: REQ (transid, key)
       B-->>A: ACK (transid)
       B-->>A: RESP (transid, status, payload)

Discovery with a registry
~~~~~~~~~~~~~~~~~~~~~~~~~

A registry, a :ref:`core service <core-services>`, lets clients look up
services by ID instead of waiting for broadcasts.

.. mermaid::

   sequenceDiagram
       autonumber
       participant A as Peer A (client)
       participant N as Broadcast network
       participant R as Registry
       participant B as Peer B (service)
       Note over A,B: Discovery phase (broadcast + registry)
       A->>N: HELLO (broadcast): A id, reply address
       N-->>B: HELLO from A
       B->>A: HELLO (direct): B id, address
       B->>R: REGISTER: B id, address, ttl, metadata
       R-->>B: REGISTER_ACK
       A->>R: LOOKUP: B id
       R-->>A: LOOKUP_RESP: B id, address, ttl
       Note over A,B: Transaction phase (direct)
       A->>B: REQ (transid, key)
       B-->>A: ACK (transid)
       B-->>A: RESP (transid, status, payload)
       Note over A: no reply in time: timeout, log, retry

Brokered
--------

Every peer connects to a central broker, which routes by ``destid`` or by
key. No discovery phase is needed.

Publish / subscribe
~~~~~~~~~~~~~~~~~~~

.. mermaid::

   sequenceDiagram
       autonumber
       participant A as Peer A (publisher)
       participant K as Broker
       participant B as Peer B (subscriber)
       participant C as Peer C (subscriber)
       Note over K,C: Subscription phase
       B->>K: SUBSCRIBE telemetry.pos
       C->>K: SUBSCRIBE telemetry.pos
       Note over K: update match table (topic to subscribers)
       Note over A,K: Publish phase
       A->>K: PUB telemetry.pos (x 10, y 20)
       Note over K: fan out to all matches
       K-->>B: PUB telemetry.pos (x 10, y 20)
       K-->>C: PUB telemetry.pos (x 10, y 20)

Request / reply
~~~~~~~~~~~~~~~

.. mermaid::

   sequenceDiagram
       autonumber
       participant A as Peer A (client)
       participant K as Broker
       participant C as Peer C (service)
       Note over A,C: all peers connect to the broker at startup
       A->>K: REQ (destid C, transid T, key target_pos)
       Note over K: route by destid
       K->>C: REQ (sourceid A, destid C, transid T)
       C-->>K: ACK (T)
       K-->>A: ACK (T)
       Note over C: process request
       C-->>K: RESP (T, value 42.0)
       K-->>A: RESP (T, value 42.0)

Trade-offs
----------

.. list-table::
   :header-rows: 1
   :widths: 16 42 42

   * -
     - Peer-to-peer
     - Brokered
   * - Reliability
     - ✗ Hard to guarantee delivery if a peer crashes mid-transit. Retries,
       persistence and replay must come from the protocol or application.
     - ✓ Buffering, persistence, acknowledgements, retries and dead-letter
       queues come built in.
   * - Latency
     - ✓ Very low: a direct socket path with no intermediate hop.
     - ✗ Higher: every message passes through the broker, with queueing.
   * - Throughput
     - ✓ No central bottleneck. Ideal for local, tightly coupled flows.
     - ✓ Efficient routing and fan-out, with no broadcast storms at scale.
   * - Connections
     - ✗ Grow as O(N²): 32 daemons can need about 500 connections.
     - ✓ Grow as O(N): 1,000 daemons need about 1,000 connections.
   * - Peers per host
     - ✗ Roughly 30–50 before file-descriptor and kernel-memory pressure
       hurt I/O.
     - ✓ Thousands of producers and consumers can share one host.
   * - Availability
     - ✓ No single point of failure.
     - ✗ If the broker fails, everything stops unless it is clustered with
       failover.
   * - Operations and security
     - ✗ Dynamic ports, discovery traffic, firewall rules and peer
       authentication must all be managed.
     - ✓ Mature tooling for access control, monitoring and auditing.

Example transports
------------------

**Brokered: RabbitMQ.** The broker provides durable queues, acknowledgements,
retries, dead-letter queues, flexible routing (fan-out, topic, direct), and
monitoring tools. The costs are extra latency and a central dependency, which
needs clustering and failover.

**Peer-to-peer: ZeroMQ DEALER/ROUTER.** This gives very low latency, high
throughput, and flexible topologies. But nothing is persisted, there is no
replay, and no global discovery. Reliability, ordering and backpressure must
come from the protocol or the application.

What this means for bamboo
--------------------------

bamboo keeps the meaning of messages above the transport. Over a broker,
bamboo hands persistence, buffering and delivery guarantees to the broker.
Over a peer-to-peer transport, bamboo itself must provide them through ACKs,
NACKs, sequencing and state reconciliation. Operators can then pick the model
that fits each subsystem's performance, reliability and operational needs.
