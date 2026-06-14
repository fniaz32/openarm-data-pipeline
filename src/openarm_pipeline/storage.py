import h5py
import numpy as np

from openarm_pipeline.models import SyncedSample

# write a recording episode to HDF5 (keeps numeric joint arrays and image tensors together in 1 file)
class EpisodeWriter:
    def __init__(self, path: str, metadata: dict):
        self.path = path
        self.metadata = metadata
        self.samples: list[SyncedSample] = []
    def append(self, sample: SyncedSample) -> None:
        # keep samples in memory cuz small demo, longer real recordings would be chunked
        self.samples.append(sample)
    def close(self) -> None:
        # if nothing captured, no empty episode
        if not self.samples:
            return
        timestamps = np.array(
            [sample.timestamp_ns for sample in self.samples],
            dtype=np.int64,
        )
        positions = np.stack([
            sample.joint_state.positions
            for sample in self.samples
        ])
        velocities = np.stack([
            sample.joint_state.velocities
            for sample in self.samples
        ])
        torques = np.stack([
            sample.joint_state.torques
            for sample in self.samples
        ])
        with h5py.File(self.path, "w") as file:
            file.attrs["schema"] = "openarm_episode_v1"
            for key, value in self.metadata.items():
                file.attrs[key] = str(value)
            joint_group = file.create_group("joint_states")
            joint_group.create_dataset("timestamps", data=timestamps)
            joint_group.create_dataset("positions", data=positions)
            joint_group.create_dataset("velocities", data=velocities)
            joint_group.create_dataset("torques", data=torques)
            cameras_group = file.create_group("cameras")
            for camera_id in self.samples[0].frames.keys():
                camera_group = cameras_group.create_group(camera_id)
                camera_timestamps = np.array([
                    sample.frames[camera_id].timestamp_ns
                    for sample in self.samples
                ], dtype=np.int64)
                frames = np.stack([
                    sample.frames[camera_id].frame
                    for sample in self.samples
                ])
                camera_group.create_dataset(
                    "timestamps",
                    data=camera_timestamps,
                )
                camera_group.create_dataset(
                    "frames",
                    data=frames,
                    compression="gzip",
                )