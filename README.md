# touch-up
Image pre-processing module to enhance text and redact pii

## About
Part of a processing pipeline to more accurately use NLP to answer questions about images

## Example
```py
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse

from touch_up.datauri import create_datauri_from_bytes
from touch_up.image import should_preprocess_from_datauri, enhance_image_from_datauri
from touch_up.pii import redact_from_datauri

import asyncio

app = FastAPI()

executor = ProcessPoolExecutor(max_workers=cpu_count())

@app.post("/", response_class=PlainTextResponse)
async def enhance_and_redact(file: UploadFile = File(...)) -> str:
    content = await file.read()
    du = create_datauri_from_bytes(content, file.content_type)

    loop = asyncio.get_running_loop()

    if should_preprocess_from_datauri(du):
        result = await loop.run_in_executor(
            executor,
            redact_from_datauri,
            enhance_image_from_datauri(du)
        )
    else:
        result = await loop.run_in_executor(
            executor,
            redact_from_datauri,
            du
        )

    return result
```