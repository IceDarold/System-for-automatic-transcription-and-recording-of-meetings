def speaker_segments(audio_path: str) -> list:
    return [
        {
            "speaker": "A",
            "start": 0.0,
            "end": 10.0,
            "text": "Заглушка: текст спикера A"
        },
        {
            "speaker": "B",
            "start": 10.0,
            "end": 20.0,
            "text": "Заглушка: текст спикера B"
        }
    ]
