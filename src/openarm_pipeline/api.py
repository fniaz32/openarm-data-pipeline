from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openarm_pipeline.can_setup import setup_commands
from openarm_pipeline.recorder import RecordingController

# tags recording w/ user
class RecordingRequest(BaseModel):
    operator: str = "unknown"
    task: str = "demo"

# global controller owns CAN reader sim, camers, sync logic, recording state
app = FastAPI(title="OpenArm Data Collection API")
controller = RecordingController()

@app.on_event("startup")
def startup():
    # start bg loop once API starts so status is current
    controller.start_loop()

@app.get("/health")
def health():
    return {"ok": True}

# if hardware, setup (i did not have hardware)
@app.get("/can/setup-commands")
def can_setup_commands():
    return {
        "note": "Run these on real OpenArm hardware before recording.",
        "commands": setup_commands(),
    }

@app.get("/status")
def status():
    return controller.status()

@app.post("/recordings/start")
def start_recording(request: RecordingRequest):
    try:
        episode_id = controller.start_recording(
            operator=request.operator,
            task=request.task,
        )
        return {"episode_id": episode_id}
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error))


@app.post("/recordings/stop")
def stop_recording():
    try:
        episode_id = controller.stop_recording()
        return {"episode_id": episode_id}
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error))

@app.get("/episodes")
def list_episodes():
    episode_dir = Path("data/episodes")
    episode_dir.mkdir(parents=True, exist_ok=True)
    return [
        {
            "filename": path.name,
            "download_url": f"/episodes/{path.name}/download",
        }
        for path in episode_dir.glob("*.h5")
    ]

# read episode data without downloadinge full recording
@app.get("/episodes/{filename}/metadata")
def episode_metadata(filename: str):
    path = Path("data/episodes") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Episode not found")
    import h5py
    with h5py.File(path, "r") as file:
        attrs = {
            key: value
            for key, value in file.attrs.items()
        }
        sample_count = len(file["joint_states"]["timestamps"])
    return {
        "filename": filename,
        "metadata": attrs,
        "sample_count": sample_count,
    }

@app.get("/episodes/{filename}/download")
def download_episode(filename: str):
    path = Path("data/episodes") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Episode not found")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=filename,
    )

# serve browser dashboard from dashboard folder
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")