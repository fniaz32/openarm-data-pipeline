from dataclasses import dataclass
import numpy as np

# shared data containers passed between CAN reader, camera simulator, synchronizer, recorder, and storage layer

@dataclass
class JointState:
    timestamp_ns: int
    positions: np.ndarray
    velocities: np.ndarray
    torques: np.ndarray

@dataclass
class CameraFrame:
    timestamp_ns: int
    camera_id: str
    frame: np.ndarray
    sequence: int

# 1 training sample: joint state + closest camera frames atm
@dataclass
class SyncedSample:
    timestamp_ns: int
    joint_state: JointState
    frames: dict[str, CameraFrame]