import subprocess
import modal
import requests
import os
import re
from urllib.parse import urlparse, unquote

LINKS = [
    "https://civitai.com/api/download/models/123456?type=Model&format=SafeTensor",
    # Add more model download links as needed
]
PORT = 7860

framepack_image = (
    modal.Image.from_registry("nvidia/cuda:12.6.0-devel-ubuntu22.04", add_python="3.10")
    .apt_install("wget", "git", "libgl1-mesa-glx", "libglib2.0-0")
    .pip_install(
        "accelerate==1.6.0",
        "diffusers==0.33.1",
        "transformers==4.46.2",
        "gradio==5.25.2",
        "sentencepiece==0.2.0",
        "pillow==11.1.0",
        "av==12.1.0",
        "numpy==1.26.2",
        "scipy==1.12.0",
        "requests==2.31.0",
        "torchsde==0.2.6",
        "jinja2>=3.1.2",
        "einops",
        "opencv-contrib-python-headless==4.10.0.84",
        "safetensors",
        "peft",
        "torch==2.6.0",
        "torchvision==0.21.0",
        "hf_transfer",
        "ninja",
        "packaging",
        "hf_transfer",
        "triton",
        "xformers",
        "sageattention",
    )
    
    .run_commands(
        "pip install flash-attn --no-build-isolation",

    )
    .run_commands(
        "cd root && git clone https://github.com/colinurbs/FramePack-Studio.git",
        "mkdir -p root/FramePack-Studio/outputs root/FramePack-Studio/loras",
    )
)

# Create volumes
MODEL_PATH = "/root/FramePack-Studio/hf_download"  # Where the Volume will appear in the container
model_volume = modal.Volume.from_name("hf_download", create_if_missing=True)
OUTPUT_PATH = "/root/FramePack-Studio/outputs"
output_volume = modal.Volume.from_name("fp_outputs", create_if_missing=True)
TEMP_PATH = "/root/FramePack-Studio/temp"
temp_volume = modal.Volume.from_name("fp_temp", create_if_missing=True)
LORA_PATH = "/root/FramePack-Studio/loras"
lora_volume = modal.Volume.from_name("lora", create_if_missing=True)

# Add environment variables to the image.
image = framepack_image.env({
    "HF_HUB_ENABLE_HF_TRANSFER": "1",  # faster downloads
    "HF_HUB_CACHE": MODEL_PATH,
})

# Initialize the Modal app with the image that includes environment variables.
app = modal.App("framepack", image=image)

def download_loras(api_key):
    """Download loras if they don't exist in the volume"""
    os.makedirs(LORA_PATH, exist_ok=True)

    for link in LINKS:
        # Add API token to URL
        parsed = urlparse(link)
        query = parsed.query
        if query:
            new_query = f"{query}&token={api_key}"
        else:
            new_query = f"token={api_key}"
        download_url = parsed._replace(query=new_query).geturl()
        
        try:
            # Get filename from Content-Disposition header
            with requests.get(download_url, stream=True, timeout=60) as response:
                response.raise_for_status()
                
                # Extract filename from headers or URL
                if "content-disposition" in response.headers:
                    content_disposition = response.headers["content-disposition"]
                    filename = re.findall(r'filename=(?:"([^"]+)"|([^;]+))', content_disposition)[0][0]
                else:
                    filename = os.path.basename(parsed.path)
                
                # Clean filename from URL encoding
                filename = os.path.basename(filename)  # Remove path components
                filename = unquote(filename)  # Decode URL-encoded characters
                filepath = os.path.join(LORA_PATH, filename)
                
                if os.path.exists(filepath):
                    print(f"✓ {filename} already exists")
                    continue
                
                print(f"⏳ Downloading {filename}...")
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                lora_volume.commit()
                print(f"✅ Successfully downloaded {filename}")
                
        except Exception as e:
            print(f"❌ Failed to download {filename}: {str(e)}")

@app.function(
    secrets=[modal.Secret.from_name("civitai-token")],
    gpu="a10g",
    cpu=2,
    memory=1024,
    timeout=600,
    min_containers=1,  # Keep at least one instance of the server running.
    max_containers=1,
    volumes={
        OUTPUT_PATH: output_volume, 
        MODEL_PATH: model_volume,
        TEMP_PATH: temp_volume,
        LORA_PATH: lora_volume,
    },
)
@modal.concurrent(max_inputs=100)
@modal.web_server(port=PORT, startup_timeout=300)
def ui():
    """Start Framepack web interface"""
    # Download models before starting the UI
    apikey=os.environ["CIVITAI_API"]
    download_loras(apikey)
    
    framepack_path = "/root/FramePack-Studio/studio.py"
    framepack_command = (
        f"python {framepack_path} "
        f"--server 0.0.0.0 --port {PORT}"
    )
    subprocess.Popen(framepack_command, shell=True)
