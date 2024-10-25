import os
import tempfile
import asyncio
from postprocessing import post_processing

def transcribe_chunk_en(model, file_path):
    """
    Transcribes a chunk of audio file in English using the specified model.

    Args:
        model (Model): The model used for transcription.
        file_path (str): The path to the audio file.

    Returns:
        str: The transcribed text.

    Raises:
        Exception: If an error occurs during transcription.

    """
    try:
        segments, info = model.transcribe(
            file_path,
            beam_size=5,
            language="en",
            condition_on_previous_text=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=300),
        )
        transcription = ''.join(segment.text for segment in segments)
        return transcription
    except Exception as e:
        print(f"Error in transcribing chunk (English): {e}")
        return ""

def transcribe_chunk_vi(model, file_path):
    """
    Transcribes a chunk of audio file in Vietnamese using the specified model.

    Args:
        model (Model): The model used for transcription.
        file_path (str): The path to the audio file.

    Returns:
        str: The transcribed text.

    Raises:
        Exception: If an error occurs during transcription.

    """
    try:
        segments, info = model.transcribe(
            file_path,
            # beam_size=3,
            # best_of=3,
            # patience = 2,
            repetition_penalty = 2,
            no_speech_threshold= 0.5,
            # temperature= 0.1,
            language="vi",
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=200),
        )
        transcription = ''.join(segment.text for segment in segments)
        return transcription
    except Exception as e:
        print(f"Error in transcribing chunk (Vietnamese): {e}")
        return ""

async def transcribe_audio(recorder, websocket, chunk_time, model, language):
    """
    Transcribes audio in real-time and sends the transcription over a websocket.

    Args:
        recorder (Recorder): The audio recorder object.
        websocket (WebSocket): The websocket connection object.
        chunk_time (float): The time interval between each audio chunk.
        model (str): The path to the language model used for transcription.
        language (str): The language of the audio ('vi' for Vietnamese, 'en' for English).

    Returns:
        None
    """
    while recorder.recording:
        try:
            await asyncio.sleep(chunk_time)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk_file:
                chunk_file = temp_chunk_file.name
            recorder.save_chunk_to_file(chunk_file)

            transcription = transcribe_chunk_vi(model, chunk_file) if language == 'vi' else transcribe_chunk_en(model, chunk_file)

            os.remove(chunk_file)
            transcription = post_processing(transcription)
            if transcription:
                print(f"Transcription: {transcription}")
                await websocket.send_json({'text': transcription})
        except Exception as e:
            print(f"Error during transcription: {e}")
            await websocket.send_json({'error': str(e)})