from modal import App, Image, asgi_app

app = App("corn-kernel-detector")

image = (
    Image.debian_slim()
    .pip_install("ultralytics", "opencv-python", "fastapi", "uvicorn", "numpy", "pillow", "modal", "python-multipart")
    .apt_install("libglib2.0-0", "libgl1")
    .add_local_file("api/kernel_api.py", remote_path="/app/kernel_api.py")
    .add_local_file("models/best.pt", remote_path="/app/best.pt")
)

@app.function(
    image=image,
    timeout=300,
    scaledown_window=300
)
@asgi_app()
def fastapi_app():
    import sys
    sys.path.append("/app")
    import kernel_api
    return kernel_api.app
