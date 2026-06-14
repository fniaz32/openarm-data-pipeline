import threading
import time
import uuid
from pathlib import Path

from openarm_pipeline.camera_sim import make_default_cameras
from openarm_pipeline.can_reader import MockCANReader
from openarm_pipeline.storage import EpisodeWriter
from openarm_pipeline.sync import TimestampAligner

# coordinates full pipeline: read CAN, capture camera, match  timestamps, write synced samples when recording
class RecordingController:
    def __init__(self):
        self.camera_ids = [
            "wrist_left",
            "wrist_right",
            "ceiling",
            "zed_left",
            "zed_right",
        ]
        self.can_reader = MockCANReader(joint_count=8)
        self.cameras = make_default_cameras()
        self.aligner = TimestampAligner(self.camera_ids)
        self.running = False
        self.recording = False
        self.writer = None
        self.thread = None
        self.latest_joint = None
        self.sample_count = 0
        self.current_episode_id = None
    def start_loop(self):
        if self.running:
            return
        self.running = True
        # acquisition run in background thread to keep FastAPI endpoints responsive
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()
    def loop(self):
        while self.running:
            self.step()
            time.sleep(0.01)
    def step(self):
        now = time.perf_counter()
        # collect due camera frames based on fps
        for camera in self.cameras:
            if camera.ready(now):
                frame = camera.capture(now)
                self.aligner.add_frame(frame)
        # read latest joint state and use as timestamp anchor for alignment
        joint_state = self.can_reader.read()
        self.latest_joint = joint_state
        synced = self.aligner.align(joint_state)
        # only write complete synced samples so every row has joints and all camera views
        if synced is not None and self.recording:
            self.writer.append(synced)
            self.sample_count += 1
    def start_recording(self, operator: str = "unknown", task: str = "demo"):
        if self.recording:
            raise RuntimeError("Already recording")
        Path("data/episodes").mkdir(parents=True, exist_ok=True)
        episode_id = f"episode_{uuid.uuid4().hex[:8]}"
        path = f"data/episodes/{episode_id}.h5"
        # metadata stored directly into HDF5 file
        metadata = {
            "episode_id": episode_id,
            "operator": operator,
            "task": task,
            "simulated": True,
            "can_interfaces": "can0,can1",
        }
        self.writer = EpisodeWriter(path, metadata)
        self.recording = True
        self.sample_count = 0
        self.current_episode_id = episode_id
        return episode_id
    def stop_recording(self):
        if not self.recording:
            raise RuntimeError("Not recording")
        self.recording = False
        self.writer.close()
        self.writer = None
        finished = self.current_episode_id
        self.current_episode_id = None
        return finished
    def status(self):
        latest_positions = None
        latest_velocities = None
        latest_torques = None
        # convert numpy to lists so that FastAPI can JSON
        if self.latest_joint is not None:
            latest_positions = self.latest_joint.positions.tolist()
            latest_velocities = self.latest_joint.velocities.tolist()
            latest_torques = self.latest_joint.torques.tolist()
        return {
            "recording": self.recording,
            "sample_count": self.sample_count,
            "current_episode_id": self.current_episode_id,
            "simulated_can": True,
            "can_interfaces": ["can0", "can1"],
            "camera_ids": self.camera_ids,
            "latest_joint_state": {
                "positions": latest_positions,
                "velocities": latest_velocities,
                "torques": latest_torques,
            },
        }