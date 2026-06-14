OpenArm 2.0 Data Collection Pipeline
Overview

This project is a simulated data collection pipeline for the OpenArm 2.0 robotic arm. The goal was to build an end-to-end system that can collect robot state information and camera observations, synchronize them, and store them as structured episodes for later use in robot learning workflows.

Since I didn't have access to a physical OpenArm system, I implemented the full pipeline using simulated CAN data and camera feeds. The architecture was designed so that the simulated components can be replaced with real hardware integrations later with minimal changes.

The project includes:

OpenArm CAN setup scripts
Simulated CAN telemetry (joint position, velocity, torque)
Multi-camera simulation
Timestamp-based synchronization
HDF5 episode storage
FastAPI backend
Browser-based monitoring dashboard
Tasks Completed
1. CAN Interface Setup

I included scripts that follow the OpenArm CAN setup workflow described in the documentation.

Example commands:

openarm-can-cli -i can0 can_configure
openarm-can-cli -i can1 can_configure

openarm-can-cli -i can0 set_zero
openarm-can-cli -i can1 set_zero

Files:

scripts/setup_can.sh
scripts/verify_can.sh

These scripts document the expected initialization process for CAN-FD communication and motor zeroing.

I wasn't able to verify the setup against a real arm, so I couldn't provide actual terminal output showing the interfaces online or the motors being zeroed.

2. CAN Data Reading

To simulate robot telemetry, I implemented a mock CAN reader that continuously generates:

Joint positions
Joint velocities
Joint torques

The values follow smooth sinusoidal motion profiles so the data behaves more like a moving robot instead of random noise.

The interface is intentionally simple and mirrors what a real CAN-backed implementation would expose, making it easy to swap in actual hardware communication later.

3. Multi-Camera Synchronization

The pipeline simulates the following camera streams:

Left wrist camera
Right wrist camera
Ceiling camera
ZED left camera
ZED right camera

(Representing the stereo ZED as separate left/right image streams.)

Each camera produces timestamped frames independently and can run at different frame rates.

For synchronization, I used a timestamp-based nearest-neighbor approach:

Joint states act as the reference timeline.
For every joint state sample, the closest frame from each camera is selected.
If any camera frame falls outside a configurable timing tolerance, the sample is discarded.

This keeps the implementation simple while still producing synchronized training data.

4. Data Storage Backend

Episodes are stored as HDF5 files.

I chose HDF5 because it works well for machine learning datasets and allows structured storage of both numerical robot state data and image observations in a single file.

Some benefits include:

Efficient storage for large datasets
Native NumPy support
Hierarchical organization
Built-in compression support

Each episode contains:

joint_states/
    timestamps
    positions
    velocities
    torques

cameras/
    wrist_left/
    wrist_right/
    ceiling/
    zed_left/
    zed_right/

Episode metadata is stored directly in the file as HDF5 attributes.

REST API

The backend exposes endpoints for:

GET  /episodes
GET  /episodes/{filename}/metadata
GET  /episodes/{filename}/download

These endpoints allow recorded episodes to be listed, inspected, and downloaded.

5. Monitoring Dashboard

I implemented a lightweight dashboard that communicates with the backend through the REST API.

The dashboard provides:

Current recording status
Live joint state information
Episode listing
Start recording control
Stop recording control
Visibility into CAN setup commands

The UI is intentionally simple since the focus of the project was the data pipeline itself rather than frontend development.

Architecture

The data flow looks like this:

CAN Reader
      |
      v
 JointState

Camera Simulator
      |
      v
 CameraFrame

Timestamp Aligner
      |
      v
 SyncedSample

Episode Writer (HDF5)
      |
      v
 Episode File

FastAPI Backend
      |
      v
 Dashboard

Each component has a single responsibility, which keeps the system easier to maintain and makes it straightforward to replace simulated components with hardware-backed implementations later.

Design Decisions
Simulation-First Approach

Since I didn't have access to OpenArm hardware, I chose to build and validate the entire pipeline using simulated data sources.

This allowed me to focus on the overall architecture, synchronization logic, storage format, and API design while still keeping the interfaces realistic.

Timestamp-Based Synchronization

I used nearest-neighbor timestamp alignment because it is:

Simple
Easy to reason about
Easy to test
A common baseline approach in robotics systems

If hardware access were available, more advanced synchronization methods such as hardware triggers or synchronized clocks could be explored.

HDF5 Storage

I selected HDF5 over alternatives such as custom formats or MCAP because the primary goal was creating structured machine learning datasets.

HDF5 makes it easy to store:

Robot state arrays
Image tensors
Metadata

all within a single portable file.

Trade-Offs
Prioritized
Clear system architecture
End-to-end functionality
Simplicity
Ease of extension
Readability
Not Prioritized
Photorealistic camera simulation
High-performance streaming
Hardware-specific optimizations
Advanced frontend design
What I Would Do Next

With access to physical hardware and additional development time, I would:

Replace the simulated CAN reader with the OpenArm CAN interface
Integrate real Arducam and ZED camera drivers
Add live image streaming to the dashboard
Replace polling with WebSocket-based telemetry updates
Support configurable synchronization strategies
Add dataset export and conversion tools for downstream training pipelines
Move episode writing to chunked/incremental storage for larger recordings
Running the Project

Install dependencies:

pip install -r requirements.txt

Start the API:

python -m uvicorn openarm_pipeline.api:app --reload --app-dir src

Open:

http://127.0.0.1:8000

The dashboard will be available in the browser.

Notes

A physical OpenArm robot was not available during development, so all CAN telemetry and camera data are simulated.

I tried to keep the simulated interfaces as close as possible to what a real implementation would require, so the overall architecture and data flow should translate cleanly to a hardware-backed version.