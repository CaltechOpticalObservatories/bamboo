from __future__ import annotations
from datetime import datetime, timezone
import re
import uuid
from typing import Optional, Dict, Any, Iterable

from .message import Envelope, Message, MsgType

class MessageBuilder:
    """
    Builder that always produces a valid Message
    with the exact envelope fields. It also enforces key rules:
     - Direct messages (destid set) of type GET/SET/REQ/CONFIG should have a 'key'
    - Broadcast (destid=None): 'key' is used as the PUB/SUB topic
    """
    def __init__(self, sourceid: str, version: int = 1):
        self._env: Dict[str, Any] = {
            "version":  version,
            "type":     MsgType.REQ,
            "transid":  _uuid(),
            "key":      None,
            "payload":  {},
            "time":     _now_iso(),
            "destid":   None,
            "sourceid": sourceid,
            "traceparent": None,
            "tracestate":  None,
        }
        self._binary: Optional[bytes] = None

    def req(self, key: str, payload: Dict[str, Any]):
        self._env["type"]    = MsgType.REQ
        self._env["key"]     = key
        self._env["payload"] = payload
        return self

    def resp(self, transid: str, payload: Dict[str, Any], key: Optional[str] = None):
        self._env["type"]     = MsgType.RESP
        self._env["transid"]  = transid
        self._env["key"]      = key
        self._env["payload"]  = payload
        return self

    def ack(self, transid: str):
        self._env["type"]     = MsgType.ACK
        self._env["transid"]  = transid
        self._env["payload"]  = {"ack": transid}
        return self

    def config(self, key: str, payload: Dict[str, Any], persist: bool = True):
        self._env["type"]    = MsgType.CONFIG
        self._env["key"]     = key
        self._env["payload"] = {"persist": persist, "data": payload}
        return self

    def hello(self, *, caps: Iterable[str], keys: Iterable[str], subs: Iterable[str], rev: int, ts: float):
        self._env["type"] = MsgType.HELLO
        self._env["key"] = "bamboo.hello"
        self._env["payload"] = {
            "caps": sorted(set(caps)),
            "keys": sorted(set(keys)),
            "subs": sorted(set(subs)),
            "rev": int(rev),
            "ts": ts,
            "noresp": True,
        }
        return self

    def pub(self, topic: str, payload: Dict[str, Any]):
        self._env["type"] = MsgType.PUB
        self._env["key"] = topic
        self._env["payload"] = payload
        return self

    def subscribe(self, add: Iterable[str] = (), remove: Iterable[str] = ()):
        self._env["type"] = MsgType.SUBSCRIBE
        self._env["key"] = "bamboo.subscribe"
        self._env["payload"] = {
            "add": sorted(set(add)),
            "remove": sorted(set(remove)),
            "noresp": True,
        }
        return self

    def to(self, destid: Optional[str]):
        self._env["destid"] = destid
        return self

    # W3C Trace Context, e.g. from opentelemetry.propagate.inject(carrier)
    def trace(self, traceparent: Optional[str], tracestate: Optional[str] = None):
        if traceparent is not None and not _valid_traceparent(traceparent):
            raise ValueError(f"Invalid W3C traceparent: {traceparent!r}")
        self._env["traceparent"] = traceparent
        self._env["tracestate"]  = tracestate if traceparent is not None else None
        return self

    def json(self, payload: Dict[str, Any]):
        self._env["payload"] = payload
        return self

    def binary(self, data: bytes):
        self._binary = data
        return self

    # If this is a direct message, you have to supply a key
    def build(self) -> Message:
        # Direct REQ/CONFIG/PUB must have a key (topic/handler)
        from .message import MsgType as MT
        if self._env["destid"] is not None and self._env["type"] in {MT.REQ, MT.CONFIG, MT.PUB} and not self._env["key"]:
            raise ValueError("Direct REQ/CONFIG/PUB require a 'key' (topic/handler).")
        return Message(Envelope(**self._env), self._binary)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _uuid() -> str:
    return uuid.uuid4().hex

# version-traceid-parentid-flags, lowercase hex
_TRACEPARENT_RE = re.compile(r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")

def _valid_traceparent(value: str) -> bool:
    m = _TRACEPARENT_RE.match(value)
    if not m:
        return False
    version, trace_id, parent_id, _ = m.groups()
    return version != "ff" and trace_id != "0" * 32 and parent_id != "0" * 16