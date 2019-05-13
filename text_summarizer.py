from gensim.summarization import summarize


def summarize_text(text_data, ratio):
    if ratio > 1 :
        ratio = 0.5
    
    transcription_summary = summarize(text_data, ratio=ratio)
    return transcription_summary


