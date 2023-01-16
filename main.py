import speech_recognition as sr
import pvporcupine
import pyaudio
import os
import openai
import requests
import time
import struct
import pyttsx3

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

while True:


    porcupine = None
    pa = None
    audio_stream = None
    try:
        porcupine = pvporcupine.create(keywords=["computer"], access_key="0d2cQcJwFfwBnOAaPC777IwUG+KkrGF8+mm4sVudUDKCROd2YBP8pg==")

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
                        rate=porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=porcupine.frame_length)

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("Hotword Detected")
                break
    finally:
        if porcupine is not None:
            porcupine.delete()

        if audio_stream is not None:
            audio_stream.close()

        if pa is not None:
                pa.terminate()

    r = sr.Recognizer()
    mic = sr.Microphone(device_index=12)
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    # audio_file = sr.AudioFile('audio.wav')
    # with audio_file as source:
    #     r.adjust_for_ambient_noise(source)
    #     audio = r.record(source)

    try:
        start = time.time()
        print("converting to text")
        transcript = r.recognize_google(audio, show_all=True, with_confidence=True)

        print("speech to text completed in:", round(time.time() - start), "seconds")

        text = transcript["alternative"][0].get("transcript")
        confidence = transcript["alternative"][0].get("confidence")

        print("speech to text:", text, "with", confidence,"confidence")

    except:
        print("error occured with speech_recognition")

    # speech not intelligible enough
    if confidence < 0.60:
        print("speech confidence too low, please repeat")

    else:
        # COMPLETION AI WITH OPENAI API
        start = time.time()
        print("generating response")
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=text,
          temperature=0.9,
          max_tokens=500,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        print("querry completed in:", round(time.time() - start), "seconds")
        answer = response.get("choices")[0].get("text")
        print(answer)

    engine = pyttsx3.init()
    # engine.setProperty("rate", 210)
    voices = engine.getProperty("voices")
    
    engine.setProperty("voice", voices[1].id)
    engine.say(answer)
    # play the speech
    engine.runAndWait()