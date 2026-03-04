import whisper
import os

model = whisper.load_model("base")

AUDIO_FOLDER = "dataset/onboarding"

def transcribe(file_path):
    print(f"Transcribing {file_path}")
    result = model.transcribe(file_path)
    text = result["text"]

    txt_path = file_path.rsplit(".", 1)[0] + ".txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved transcript to {txt_path}")

if __name__ == "__main__":
    for file in os.listdir(AUDIO_FOLDER):
        if file.endswith((".m4a", ".mp3", ".wav", ".mp4")):
            transcribe(os.path.join(AUDIO_FOLDER, file))