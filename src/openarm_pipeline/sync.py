from collections import deque

from openarm_pipeline.models import CameraFrame, JointState, SyncedSample

# matches each joint with closest frame from all cameras
class TimestampAligner:
    def __init__(self, camera_ids: list[str], tolerance_ms: float = 80):
    # 80ms should be loose enough for simmed mixed-FPS cameras while still rejecting stale frames
        self.tolerance_ns = int(tolerance_ms * 1_000_000)
        self.buffers = {
            camera_id: deque(maxlen=100)
            for camera_id in camera_ids
        }
    def add_frame(self, frame: CameraFrame) -> None:
        self.buffers[frame.camera_id].append(frame)
    def align(self, joint_state: JointState) -> SyncedSample | None:
        selected = {}
        for camera_id, buffer in self.buffers.items():
            if not buffer:
                return None
            # pick nearest frame time-wise for camera relative to joint timestamp
            closest = min(
                buffer,
                key=lambda frame: abs(
                    frame.timestamp_ns - joint_state.timestamp_ns
                ),
            )
            difference = abs(closest.timestamp_ns - joint_state.timestamp_ns)
            # if camera too far, skip instead of saving bad alignment
            if difference > self.tolerance_ns:
                return None
            selected[camera_id] = closest
        return SyncedSample(
            timestamp_ns=joint_state.timestamp_ns,
            joint_state=joint_state,
            frames=selected,
        )