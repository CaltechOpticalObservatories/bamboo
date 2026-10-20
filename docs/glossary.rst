Glossary
========

.. glossary::
   :sorted:

   ACK
      Acknowledgment. Sent by a receiver to confirm it received a message. In
      bamboo, sent as soon as a direct message passes key gating, before the
      handler runs.

   At-least-once
      A delivery guarantee: messages are retried until acknowledged. Nothing
      is lost, but a message may arrive more than once.

   Backpressure
      A signal from a busy system, such as a broker, telling senders to slow
      down when its buffers are full.

   Binary attachment
      Raw bytes sent alongside a message's JSON body, for example a
      compressed detector frame.

   Broker
      A central intermediary that receives messages from producers and routes
      them to consumers.

   Capability
      A string a peer advertises to say which features it supports, for
      example ``json``.

   Core service
      A long-lived daemon that provides observatory-wide infrastructure,
      such as a discovery registry, and must be present in every deployment.

   Dead-letter queue
      A broker queue that holds messages which could not be delivered.

   Discovery
      How peers find and identify each other, typically by broadcast,
      multicast, or a registry.

   Dying gasp
      A final, high-priority message a node sends just before it shuts down
      because of a fatal error.

   Envelope
      The structured metadata around a message's payload: type, transaction
      ID, key, source, destination, time and trace context.

   Fan-out
      Delivering one message to many subscribers.

   Fire-and-forget
      Sending without acknowledgements or retries. Used for low-latency
      telemetry.

   Frame
      One serialized message as handed to the transport: the envelope plus
      an optional binary attachment.

   Heartbeat
      A periodic message showing that a node is still alive.

   Idempotency
      The property that applying an operation more than once has the same
      effect as applying it once. This prevents duplicate commands when
      messages are retried.

   Key
      The name of a handler on a peer, such as ``camera.capture``. For
      ``PUB`` messages, the key is the topic.

   LVC
   Last value cache
      Keeps the latest message on each topic and sends it immediately to a
      subscriber that joins late.

   MTU
      Maximum transmission unit. The largest frame a transport will carry.

   NACK
      Negative acknowledgment. Tells the sender that a message in a sequence
      was missing or corrupted.

   Peer
      Any participant in a bamboo network, identified by a unique ID.

   Peer-to-peer
   P2P
      A decentralized model where nodes connect directly, with no broker.

   Pub/sub
      Publish/subscribe. Publishers send messages on topics without knowing
      who will receive them; subscribers receive the topics they asked for.

   QoS
      Quality of service. A level of delivery guarantee, from
      fire-and-forget to strictly ordered.

   Req/rep
      Request/reply. A sender sends a request and waits for a matching
      response.

   Split-brain
      A failure in which a network partition leaves two groups of nodes,
      each believing it is in charge.

   SPOF
      Single point of failure. For example, a broker with no cluster.

   Store-and-forward
      Holding messages locally while disconnected and sending them once the
      connection returns.

   Telemetry
      Data recorded automatically and sent from sensors or instruments for
      monitoring.

   Trace context
   traceparent
      W3C Trace Context fields (``traceparent``, ``tracestate``) carried in
      the envelope so OpenTelemetry can link spans across peers. Responses
      and ACKs copy them from the request.

   Transaction ID
   transid
      A unique ID on every message. Responses and ACKs reuse it, which lets
      one operation be traced across systems.

   Transport
      The layer that physically moves frames between peers, such as Zyre,
      ZeroMQ or a broker.

   Transport agnostic
      Independent of the transport. A bamboo message means the same thing
      over any transport.
