# Known Issue

Due to how the outputs are structured, the web ui will encounter an error after a full sampling steps. Still figuring that out.

# FramePack-Studio Deployment for Modal.com

A GPU-accelerated AI media generation platform deployed via Modal. Features model management, LoRA downloads, and a Gradio web interface.

## Features

- GPU-accelerated inference (NVIDIA A10G)
- Automatic CivitAI LORA downloads
- Web UI with Gradio interface
- Persistent storage with Modal volumes
- Secure API key management

## Installation
1. **Register an account at [Modal](https://modal.com)** (Free $30/month credit if you provide a payment detail)

2. **Install Modal CLI**
   ```bash
   pip install modal
   modal token new
   ```

2. **Clone this repo**
   ```bash
   git clone https://github.com/hazumin/framepack-studio-modal-deploy.git
   cd framepack-studio-modal-deploy
   ```

3. **Set up secrets**
   - Add CivitAI API token to Modal:
   ```bash
   modal secret create civitai-token CIVITAI_API=<your-api-key>
   ```

## Usage

1. **Deploy to Modal**
   ```bash
   modal deploy framepack-studio.py
   ```
   - First time running will take 10-20 minutes, consecutive runs will take seconds due to Modal persistent volumes.

2. **Access Web UI**
   - After deployment, Modal will provide a URL
   - Access via browser at `https://<your-app-name>-modal-app.modal.run`
   - Accessing the UI for the first time will trigger the downloads for the required models, it's normal to wait for a few minutes to download the models.
   - Additionally, check the app logs for current job status. `https://modal.com/apps/<your-username>/main/<app-id>`

## Configuration

Customize `framepack-studio.py`:
```python
# Add model download links
LINKS = [
    "https://civitai.com/api/download/models/123456",
    # Add more models here
]

# Hardware settings (app.function decorator)
@app.function(
    gpu="a10g",  # Change to "a100" for larger GPU
    cpu=2,       # CPU cores
    memory=1024   # RAM in MB
)
```

## Credits
Many thanks to [Lvmin Zhang](https://github.com/lllyasviel) for the original [FramePack](https://github.com/lllyasviel/FramePack) and ColinUrbs for the [fork](https://github.com/colinurbs/FramePack-Studio) this is based on!

    @article{zhang2025framepack,
        title={Packing Input Frame Contexts in Next-Frame Prediction Models for Video Generation},
        author={Lvmin Zhang and Maneesh Agrawala},
        journal={Arxiv},
        year={2025}
    }
