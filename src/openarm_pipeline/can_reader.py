import time
import numpy as np

from openarm_pipeline.models import JointState

# no hardware so simulated data returning same fields as real CAN reader
class MockCANReader:
    def __init__(self, joint_count: int = 8):
        self.joint_count = joint_count
        self.start_time = time.time()
    # smooth sine waves so that it looks like actual joint movement instead of noise
    def read(self) -> JointState:
        elapsed = time.time() - self.start_time
        joints = np.arange(self.joint_count)
        positions = np.sin(elapsed + joints)
        velocities = np.cos(elapsed + joints)
        torques = 0.1 * np.sin(elapsed + joints)
        return JointState(
            # monotonic better for sync cuz no jump if system time changes
            timestamp_ns=time.monotonic_ns(),
            positions=positions,
            velocities=velocities,
            torques=torques,
        )