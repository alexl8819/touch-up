# touch-up
Image pre-processing module to enhance text and redact pii

## About
Part of a processing pipeline to more accurately use NLP to answer questions about images

## How to use
Server:
```
gunicorn api:app --worker-class asgi --timeout 60
```

Client:
```
curl -X POST "http://localhost:8000" -F "file=@sampleimage.jpg" -H "Content-Type: multipart/form-data"
```
Returns a plaintext response displaying a datauri