from __future__ import annotations
import heapq
from itertools import count
class QueueManager:
    def __init__(self): self._queue=[]; self._counter=count(); self._seen=set()
    def add(self,url,*,depth,priority=100):
        if url in self._seen: return False
        self._seen.add(url); heapq.heappush(self._queue,(priority,next(self._counter),url,depth)); return True
    def pop(self):
        _,_,url,depth=heapq.heappop(self._queue); return url,depth
    def __bool__(self): return bool(self._queue)
    def __len__(self): return len(self._queue)
