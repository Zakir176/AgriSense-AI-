from ..database import Base
from .farm import Farm
from .batch import Batch
from .reading import FeedWaterReading
from .growth import GrowthSample
from .medication import MedicationEntry
from .alert import Alert
from .media import MediaClip, InferenceResult
from .auth import User

# Ensure they are loaded to metadata
__all__ = [
    "Base",
    "Farm",
    "Batch",
    "FeedWaterReading",
    "GrowthSample",
    "MedicationEntry",
    "Alert",
    "MediaClip",
    "InferenceResult",
    "User"
]
