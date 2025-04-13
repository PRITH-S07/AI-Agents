# modal_app.py
import modal

stub = modal.Stub("llamaindex-rag-builder")
volume = modal.SharedVolume().persisted("rag-index-volume")

@stub.function(
    image=modal.Image.debian_slim().pip_install_from_requirements("requirements.txt"),
    volumes={"/root/data": volume},
    timeout=900,
    gpu="A10G"
)
def build_index():
    import inference
    inference.main("/root/data")
