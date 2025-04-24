# Speech to keystrokes

This is a tool that is able to record audio, transcribe it using Whisper and then write it out using pynput.
This is helpful for writing cursor prompts or other tools that don't have speech to text integration.

Warning! This is a key logger using pynput use at your own risk!

The default key combination is Alt-R for triggering the recording.

#### Needs these on Debian 12

> sudo apt-get install python3-dev

> sudo apt-get install portaudio19-dev