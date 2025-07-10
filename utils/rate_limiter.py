import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests, period_seconds):
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_id):
        """Checks if a client is allowed to make a request."""
        now = time.time()
        
        # Remove timestamps outside the current window
        self.requests[client_id] = [
            t for t in self.requests[client_id] 
            if now - t < self.period_seconds
        ]
        
        # Check if the number of requests is within the limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        
        return False
