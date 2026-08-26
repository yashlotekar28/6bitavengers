from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.schemas import PortalVerificationResult

class BasePortalAdapter(ABC):
    """
    Abstract Interface for Government & Regulatory Portal Adapters.
    Every adapter normalizes raw government API outputs into the Canonical PortalVerificationResult shape.
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass
    
    @abstractmethod
    async def verify(self, identifier: str, **kwargs) -> PortalVerificationResult:
        """
        Verify identifier against the official portal (or sandbox/API Setu).
        """
        pass
