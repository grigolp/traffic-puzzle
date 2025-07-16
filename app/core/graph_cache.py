import hashlib
from typing import Dict, Tuple, List, Optional
from models.graph import RoadGraph

class GraphCache:
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Tuple[RoadGraph, dict]] = {}
        self.max_size = max_size
    
    def get_cache_key(self, layout: List[List[str]]) -> str:
        """Generate hash key for layout"""
        layout_str = ''.join([''.join(row) for row in layout])
        return hashlib.md5(layout_str.encode()).hexdigest()
    
    def get(self, layout: List[List[str]]) -> Optional[Tuple[RoadGraph, dict]]:
        key = self.get_cache_key(layout)
        return self.cache.get(key)
    
    def put(self, layout: List[List[str]], graph: RoadGraph):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple LRU)
            self.cache.pop(next(iter(self.cache)))
        key = self.get_cache_key(layout)
        self.cache[key] = graph