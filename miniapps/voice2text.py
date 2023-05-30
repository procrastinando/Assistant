from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
import srt


def format_timestamp(timestamp):
    hours = int(timestamp // 3600)
    minutes = int((timestamp % 3600) // 60)
    seconds = int(timestamp % 60)
    milliseconds = int((timestamp % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_srt_files(whisper_size, file_path, languages, beam_size):
    # Transcribe audio to text
    model_size = whisper_size
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(file_path, beam_size=beam_size)

    # Generate original .srt file
    original_subs = []
    for segment in segments:
        start = srt.srt_timestamp_to_timedelta(format_timestamp(segment.start))
        end = srt.srt_timestamp_to_timedelta(format_timestamp(segment.end))
        sub = srt.Subtitle(index=segment.id,
                           start=start,
                           end=end,
                           content=segment.text)
        original_subs.append(sub)
    original_srt = srt.compose(original_subs)

    # Translate text to specified 
    translated_srts = []
    for language in languages:
        translated_subs = []
        for sub in original_subs:
            translated_text = GoogleTranslator(source='auto', target=language).translate(sub.content)
            translated_sub = srt.Subtitle(index=sub.index,
                                          start=sub.start,
                                          end=sub.end,
                                          content=translated_text)
            translated_subs.append(translated_sub)

        # Generate .srt file for each language
        translated_srt = srt.compose(translated_subs)
        translated_srts.append(translated_srt)

    return original_srt, translated_srts

