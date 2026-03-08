from __future__ import annotations
from app.infrastructure.ai.transcription.base import TranscriptionProvider, TranscriptChunkData

_SERMON_TEXTS = [
    "Good morning, church. We are so glad you are here with us today for this special service.",
    "Let us begin by giving praise to God for His goodness and mercy that endures forever.",
    "The word of the Lord says that His mercies are new every morning. Great is His faithfulness.",
    "Today we are going to be looking at the book of John chapter 3 verse 16.",
    "For God so loved the world that He gave His only begotten Son.",
    "That whosoever believeth in Him should not perish but have everlasting life.",
    "This is the foundation of our faith. This is why we gather here every week.",
    "Let me share with you a story about grace and forgiveness that changed my life.",
    "Many years ago, I was walking in darkness, lost without direction or purpose.",
    "But the Lord reached down and pulled me out of the miry clay.",
    "He set my feet on solid ground and put a new song in my mouth.",
    "The Bible tells us that we are more than conquerors through Christ who loves us.",
    "No weapon formed against you shall prosper. That is the promise of the Lord.",
    "I want you to stand on that promise today. Whatever you are going through, God is with you.",
    "The Holy Spirit is our comforter, our guide, and our strength in times of trouble.",
    "Turn with me now to Romans chapter 8 verse 28.",
    "And we know that all things work together for good to them that love God.",
    "Hold onto that promise. God is working even when you cannot see it.",
    "Let us pray together and ask the Lord to open our hearts to receive His word.",
    "May the words of my mouth and the meditation of my heart be acceptable in Thy sight, O Lord.",
]


class FakeTranscriptionProvider(TranscriptionProvider):
    async def transcribe(self, audio_path: str, duration_seconds: float = 3600.0) -> list[TranscriptChunkData]:
        chunks: list[TranscriptChunkData] = []
        n = len(_SERMON_TEXTS)
        interval = duration_seconds / n
        for i, text in enumerate(_SERMON_TEXTS):
            start = i * interval
            end = start + max(10.0, interval * 0.8)
            chunks.append(TranscriptChunkData(
                chunk_index=i,
                start_seconds=round(start, 2),
                end_seconds=round(end, 2),
                text=text,
                speaker_id="speaker_1",
                confidence=0.95,
            ))
        return chunks
