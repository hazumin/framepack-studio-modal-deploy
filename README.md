# FramePack-Studio Deployment for Modal.com

A script to deploy [FramePack-Studio](https://github.com/colinurbs/FramePack-Studio) via Modal.

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
   - Get your CivitAI API key [here](https://civitai.com/user/account)
   - Add CivitAI API token to Modal:
   ```bash
   modal secret create civitai-token CIVITAI_API=<your-api-key>
   ```

## Usage

1. **Deploy to Modal**
   ```bash
   modal deploy framepack-studio.py
   ```
   - First time running and generating will take 10-20 minutes, this only happens once.

2. **Access Web UI**
   - After deployment, Modal will provide a URL
   - Access via browser at `https://<your-app-name>-modal-app.modal.run`
   - On first time generating, it's normal to wait for a few minutes to download all the models.
   - Additionally, check the app logs for status. `https://modal.com/apps/<your-username>/main/<app-id>`

## Configuration

Customize `framepack-studio.py`:
```python
# Add model download links
LINKS = [
    "https://civitai.com/api/download/models/123456?type=Model&format=SafeTensor",
    # Add more models here
]

# Hardware settings (app.function decorator)
@app.function(
    gpu="a10g",  # Change to "a100" for larger GPU
    cpu=2,       # CPU cores
    memory=1024   # RAM in MB
)
```
![Capture](https://github.com/user-attachments/assets/a3113fb0-5cb3-48d9-97f6-f661dbc8f91d)

Make sure to get the links from here.

## Credits
Many thanks to [Lvmin Zhang](https://github.com/lllyasviel) for the original [FramePack](https://github.com/lllyasviel/FramePack) and ColinUrbs for the [fork](https://github.com/colinurbs/FramePack-Studio) this is based on!

    @article{zhang2025framepack,
        title={Packing Input Frame Contexts in Next-Frame Prediction Models for Video Generation},
        author={Lvmin Zhang and Maneesh Agrawala},
        journal={Arxiv},
        year={2025}![Capture](https://github.com/user-attachments/assets/ca511e5e-620c-4df5-827b-10ffc556970b)

    }
