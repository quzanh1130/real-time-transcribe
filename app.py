import os
import logging
import json

import torch
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel

from whisper_module import transcribe_audio
from audio_recorder import AudioRecorder
from config import MODEL_EN_NAME, MODEL_VI_NAME, DEVICE, COMPUTE_TYPE

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

recorder = AudioRecorder()
transcribe_task = None
model = None

@app.get("/")
async def get():
    """
    Handle GET requests to the root endpoint.

    Returns:
        HTMLResponse: The response containing the content of the index.html file.
    """
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time transcription.

    Args:
        websocket (WebSocket): The WebSocket connection object.

    Raises:
        WebSocketDisconnect: If the WebSocket connection is disconnected.

    Returns:
        None
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get('action')

            if action == 'start':
                global transcribe_task, model
                chunk_time = message.get('chunk_time', 1)
                language = message.get('language', 'vi')
                await websocket.send_json({'status_update': 'Loading model...'})

                try:
                    model_name = MODEL_VI_NAME if language == 'vi' else MODEL_EN_NAME
                    model = WhisperModel(model_name, device=DEVICE, compute_type=COMPUTE_TYPE)
                    # batched_model = BatchedInferencePipeline(model=model)
                except Exception as e:
                    await websocket.send_json({'status_update': f'Error loading model: {e}'})
                    continue

                recorder.start()
                transcribe_task = asyncio.create_task(transcribe_audio(recorder, websocket, chunk_time, model, language))
                await websocket.send_json({'status_update': 'Recording', 'chunk_time': chunk_time, 'language': language})

            elif action == 'stop':
                if recorder.recording:
                    recorder.stop()
                    if transcribe_task:
                        transcribe_task.cancel()
                        try:
                            await transcribe_task
                        except asyncio.CancelledError:
                            pass
                        transcribe_task = None
                        torch.cuda.empty_cache()
                    logging.info("Stopped recording")
                    await websocket.send_json({'status_update': 'Stopped'})
    except WebSocketDisconnect:
        print("Client disconnected")