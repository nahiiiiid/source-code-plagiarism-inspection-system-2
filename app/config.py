import os

class Config:
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 2 * 1024 * 1024))  # 2MB/file
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", ".py,.java,.js,.ts,.cpp,.cc,.c,.hpp,.h,.kt,.rb,.go,.php,.swift,.rs,.scala,.m,.mm,.cs,.txt").split(","))
    MODEL_NAME = os.getenv("MODEL_NAME", "mchochlov/codebert-base-cd-ft")  # CodeBERT clone-detection FT
    DEVICE = os.getenv("DEVICE", "cpu")
    SIM_THRESHOLD = float(os.getenv("SIM_THRESHOLD", "0.80"))
    TOPK_CHUNK_MATCHES = int(os.getenv("TOPK_CHUNK_MATCHES", "5"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
