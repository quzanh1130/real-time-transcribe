
def post_processing(transcription):
    if 'Thank you.' in transcription or len(transcription) < 2 or 'Thanks for watching' in transcription \
        or '�' in transcription:
        return ''
    return transcription