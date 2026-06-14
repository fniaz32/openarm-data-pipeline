OpenArm 2.0 Data Collection Pipeline

This project is a simulated data collection pipeline for the OpenArm 2.0 robotic arm.

The goal was to build an end-to-end system that can collect robot state data and camera observations, synchronize them, and store them as structured episodes that could later be used for robot learning or imitation learning workflows.

Since I did not have access to a physical OpenArm system, all CAN telemetry and camera feeds are simulated. The architecture was designed so that the simulated components can be replaced with real hardware integrations later without major changes.

Included in this project:


-> OpenArm CAN setup scripts

-> Simulated CAN telemetry (joint position, velocity, torque)

-> Multi-camera simulation

-> Timestamp-based synchronization

-> HDF5 episode storage

-> FastAPI backend

-> Browser dashboard

Tasks Completed:

CAN Interface Setup

I included scripts that follow the OpenArm CAN setup workflow described in the documentation.

Example commands:

openarm-can-cli -i can0 can_configure

openarm-can-cli -i can1 can_configure

openarm-can-cli -i can0 set_zero

openarm-can-cli -i can1 set_zero

Files:

-> scripts/setup_can.sh

-> scripts/verify_can.sh

These scripts document the expected CAN-FD initialization and motor zeroing workflow.

Because I did not have hardware access, I was not able to verify the setup against a real arm or provide terminal output showing active interfaces and successful zeroing.

CAN Data Reading

I implemented a mock CAN reader that continuously generates:

-> Joint positions

-> Joint velocities

-> Joint torques

The values follow smooth sinusoidal motion profiles so the data behaves more like a moving robot instead of random noise.

The reader exposes the same general interface that a real CAN-backed implementation would use, making it straightforward to replace with actual hardware communication later.

Multi-Camera Synchronization

The following camera streams are simulated:

-> Left wrist camera

-> Right wrist camera

-> Ceiling camera

-> ZED left camera

-> ZED right camera

(The ZED stereo camera is represented as separate left and right image streams.)

Each camera generates timestamped frames independently and can run at different frame rates.

Synchronization strategy:

-> Joint states are used as the reference timeline

-> For every joint state sample, the closest frame from each camera is selected

-> Samples are discarded if any camera frame falls outside the synchronization tolerance window

This approach is simple, deterministic, and easy to reason about while still producing synchronized training data.

Data Storage Backend

Episodes are stored as HDF5 files.

I chose HDF5 because it:

-> Works well with NumPy

-> Supports large datasets efficiently

-> Provides a structured hierarchy

-> Supports compression

-> Is commonly used in robotics and machine learning workflows

Episode structure:

joint_states/

-> timestamps

-> positions

-> velocities

-> torques

cameras/

-> wrist_left

-> wrist_right

-> ceiling

-> zed_left

-> zed_right

Episode metadata is stored directly in the HDF5 file.

REST API endpoints:

-> GET /episodes

-> GET /episodes/{filename}/metadata

-> GET /episodes/{filename}/download

These endpoints allow episodes to be listed, inspected, and downloaded.

Monitoring Dashboard

I implemented a lightweight dashboard that communicates with the backend through the REST API.

Features:

-> Current recording status

-> Live joint state information

-> Episode listing

-> Start recording button

-> Stop recording button

-> CAN setup command visibility

The dashboard is intentionally lightweight and focused on monitoring the pipeline state. A live camera preview was not implemented in this version and would be one of the first additions with more development time.

Architecture

Data flow:

CAN Reader

-> JointState

Camera Simulator

-> CameraFrame

Timestamp Aligner

-> SyncedSample

Episode Writer (HDF5)

-> Episode File

FastAPI Backend

-> Dashboard

Each component has a single responsibility which keeps the system modular and makes it easier to replace simulated components with hardware-backed implementations later.

Design Decisions

Simulation First

Since I did not have access to OpenArm hardware, I chose to build and test the entire pipeline using simulated data sources.

This allowed me to focus on the architecture, synchronization logic, storage format, and API design while keeping the interfaces realistic.

Timestamp Synchronization

I used nearest-neighbor timestamp alignment because it is:

-> Simple

-> Easy to test

-> Easy to explain

-> Commonly used as a baseline approach

If hardware access were available, more advanced synchronization methods such as hardware triggers or synchronized clocks could be explored.

HDF5 Storage

I selected HDF5 because it allows robot state data, image data, and metadata to be stored together in a single portable file while integrating naturally with NumPy-based workflows.

Assumptions

-> No physical OpenArm hardware was available during development

-> CAN telemetry is simulated

-> Camera feeds are simulated

-> The ZED stereo camera is represented as separate left and right image streams

-> Joint timestamps are treated as the reference timeline for synchronization

Trade-Offs

Prioritized:

-> Clear architecture

-> End-to-end functionality

-> Simplicity

-> Readability

-> Ease of extension

Not prioritized:

-> Photorealistic camera simulation

-> High-performance streaming

-> Hardware-specific optimization

-> Advanced frontend design

What I Would Do Next

With hardware access and additional development time I would:

-> Replace the simulated CAN reader with the OpenArm CAN interface

-> Integrate real Arducam and ZED drivers

-> Add live image streaming to the dashboard

-> Replace polling with WebSocket-based telemetry updates

-> Support configurable synchronization strategies

-> Add dataset export and conversion tools

-> Move recording storage to chunked/incremental writes for larger datasets

Running the Project

Install dependencies:

pip install -r requirements.txt

Start the API:

python -m uvicorn openarm_pipeline.api:app --reload --app-dir src

Open:

http://127.0.0.1:8000

The dashboard will be available in the browser.

Notes

Physical OpenArm hardware was not available during development, so all robot telemetry and camera data are simulated.
The goal was to keep the simulated interfaces as close as possible to what a real implementation would require so that the overall architecture and data flow could transition cleanly to hardware-backed components later.
