# Just some namespacing

from .frameprocessor import FrameProcessor
from .get_photos import get_sharp_frames_from_video

__all__ = [
    "FrameProcessor", "get_sharp_frames_from_video"
]
