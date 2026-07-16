import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SERVER = "127.0.0.1:8188"


def queue_prompt(workflow, client_id="dino-atlas"):
    payload = {"prompt": workflow, "client_id": client_id}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://{SERVER}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{SERVER}/history/{prompt_id}") as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_history(prompt_id, timeout_seconds=600):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        history = get_history(prompt_id)
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(1.5)
    raise TimeoutError(f"Timed out waiting for prompt {prompt_id}")


def load_workflow(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_workflow(path, workflow):
    Path(path).write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    workflow_path = Path(__file__).resolve().parents[1] / "workflow_templates" / "dino_sdxl_base_api.json"
    workflow = load_workflow(workflow_path)
    try:
      result = queue_prompt(workflow)
    except urllib.error.URLError as error:
      raise SystemExit(f"ComfyUI server is not reachable at http://{SERVER}. Start it first.") from error
    prompt_id = result["prompt_id"]
    print(json.dumps({"queued": result}, indent=2))
    history = wait_for_history(prompt_id)
    print(json.dumps({"history": history}, indent=2))
