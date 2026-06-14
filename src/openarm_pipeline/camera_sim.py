import time
import numpy as np

from openarm_pipeline.models import CameraFrame

# simple camera simulator used instead of the physical wrist, ceiling, and ZED cameras 
class MockCamera:
    def __init__(self, camera_id: str, fps: float):
        self.camera_id = camera_id
        self.fps = fps
        self.period_s = 1.0 / fps
        self.sequence = 0
        self.next_capture_time = 0.0
    def ready(self, now: float) -> bool:
        return now >= self.next_capture_time
    def capture(self, now: float) -> CameraFrame:
        height = 120
        width = 160
        # small rgb frame with moving white line to verify time changing frames
        image = np.zeros((height, width, 3), dtype=np.uint8)
        x = self.sequence % width
        image[:, x:x + 3, :] = 255
        # next frame based on camera fps for different cameras
        self.next_capture_time = now + self.period_s
        frame = CameraFrame(
            timestamp_ns=time.monotonic_ns(),
            camera_id=self.camera_id,
            frame=image,
            sequence=self.sequence,
        )
        self.sequence += 1
        return frame
    
# zed is in 2 streams cuz stereo
def make_default_cameras() -> list[MockCamera]:
    return [
        MockCamera("wrist_left", fps=30),
        MockCamera("wrist_right", fps=30),
        MockCamera("ceiling", fps=20),
        MockCamera("zed_left", fps=15),
        MockCamera("zed_right", fps=15),
    ]