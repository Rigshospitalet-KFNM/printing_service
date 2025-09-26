from dataclasses import dataclass, field
import socket
from typing import Optional

@dataclass
class Job:
    id: int
    printer: str
    user: str
    status: str
    pages: Optional[int] = None

@dataclass
class Printer:
    name: str
    status: str
    enabled: bool = True
    current_job: str | None = None 
    since: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    error: Optional[str] = None
    device_uri: Optional[str] = None

    def is_reachable(self, timeout: float = 2.0) -> bool:
        """
        Check if the underlying printer device is reachable
        using its device_uri (e.g. socket://172.16.80.239:9100).
        """
        if not self.device_uri:
            return False

        if self.device_uri.startswith("socket://"):
            # strip scheme
            hostport = self.device_uri[len("socket://"):]
            # split host:port (default port 9100)
            if ":" in hostport:
                host, port = hostport.split(":", 1)
                port = int(port)
            else:
                host, port = hostport, 9100

            try:
                with socket.create_connection((host, port), timeout=timeout):
                    return True
            except OSError:
                return False

        elif self.device_uri.startswith("ipp://"):
            # very simple check → try port 631 unless explicitly given
            hostport = self.device_uri[len("ipp://"):]
            if ":" in hostport:
                host, port = hostport.split(":", 1)
                port = int(port)
            else:
                host, port = hostport, 631

            try:
                with socket.create_connection((host, port), timeout=timeout):
                    return True
            except OSError:
                return False

        # unsupported scheme
        return False

