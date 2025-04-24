import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
from pynput import keyboard
from pynput.keyboard import Controller, Key
from openai import OpenAI
import time

class SpeechToKeystrokes:
    def __init__(self, modifier_key=None, trigger_key=None, api_key=None):
        self.modifier_key = modifier_key
        self.trigger_key = trigger_key
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.keyboard = Controller()
        self.modifier_pressed = False
        self.is_typing = False
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        
        # Start keyboard listener
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        
    def on_press(self, key):
        try:
            if self.is_typing:
                return
            
            # Check for modifier key
            if self.modifier_key and hasattr(key, 'name') and key.name == self.modifier_key:
                self.modifier_pressed = True
                return
            
            # Check for trigger key
            if ((self.modifier_pressed and hasattr(key, 'char') and key.char == self.trigger_key) or
                (not self.modifier_key and hasattr(key, 'name') and key.name == self.trigger_key)) and not self.is_recording:
                self.start_recording()
        except AttributeError:
            pass

    def on_release(self, key):
        if self.is_typing:
            return
        
        try:
            # Check for modifier key release
            if self.modifier_key and hasattr(key, 'name') and key.name == self.modifier_key:
                self.modifier_pressed = False
                return
            
            # Check for trigger key release
            if ((self.modifier_pressed and hasattr(key, 'char') and key.char == self.trigger_key) or
                (not self.modifier_key and hasattr(key, 'name') and key.name == self.trigger_key)) and self.is_recording:
                self.stop_recording()
        except AttributeError:
            pass

    def start_recording(self):
        print("Recording started...")
        self.is_recording = True
        self.audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_data.append(indata.copy())
        
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=callback
        )
        self.stream.start()

    def stop_recording(self):
        print("Recording stopped. Processing...")
        self.stream.stop()
        self.stream.close()
        self.is_recording = False
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                self.save_audio(temp_file.name)
                
                # Transcribe audio
                with open(temp_file.name, 'rb') as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                self.type_text(transcription.text)
            os.unlink(temp_file.name)
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            if 'temp_file' in locals() and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    def save_audio(self, filename):
        audio_data = np.concatenate(self.audio_data, axis=0)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

    def type_text(self, text):
        self.is_typing = True
        for char in text:
            self.keyboard.press(char)
            self.keyboard.release(char)
        self.is_typing = False

if __name__ == "__main__":
    # Replace with your OpenAI API key
    API_KEY = ""
    
    # Create instance with Alt-R as the hotkey combination
    stk = SpeechToKeystrokes(modifier_key='alt', trigger_key='r', api_key=API_KEY)
    
    print("Speech to Keystrokes started. Press Alt-R to start/stop recording.")
    print("Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
