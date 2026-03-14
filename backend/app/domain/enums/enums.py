from enum import Enum

class JobStage(str, Enum):
    pending = "pending"
    downloading = "downloading"
    audio_extracted = "audio_extracted"
    transcribing = "transcribing"
    transcribed = "transcribed"
    classifying = "classifying"
    classified = "classified"
    detecting_services = "detecting_services"
    services_detected = "services_detected"
    detecting_sermon = "detecting_sermon"
    sermon_detected = "sermon_detected"
    exporting_sermon = "exporting_sermon"
    sermon_exported = "sermon_exported"
    generating_highlights = "generating_highlights"
    highlights_generated = "highlights_generated"
    completed = "completed"
    failed = "failed"

class AssetType(str, Enum):
    source_video = "source_video"
    source_audio = "source_audio"
    sermon_video = "sermon_video"
    sermon_audio = "sermon_audio"
    transcript_txt = "transcript_txt"
    subtitle_srt = "subtitle_srt"
    subtitle_vtt = "subtitle_vtt"
    highlight_clip = "highlight_clip"

class SectionLabel(str, Enum):
    praise_worship = "praise_worship"
    prayer = "prayer"
    testimony = "testimony"
    offering = "offering"
    announcements = "announcements"
    sermon = "sermon"
    transition = "transition"
    other = "other"

class HighlightStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    rendered = "rendered"
