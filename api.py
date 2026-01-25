from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse

from datauri import create_datauri_from_bytes
from image import should_preprocess_from_datauri, enhance_image_from_datauri
from pii import redact_from_datauri

app = FastAPI()

@app.post("/", response_class=PlainTextResponse)
async def enhance_and_redact(file: UploadFile = File(...)):
    content = await file.read()
    du = create_datauri_from_bytes(content, file.content_type)
    return redact_from_datauri(enhance_image_from_datauri(du)) if should_preprocess_from_datauri(du) else redact_from_datauri(du)