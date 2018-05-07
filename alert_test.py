#!/usr/bin/env python3

import pyaudio
from pydub import AudioSegment
from pydub.generators import Sine
from pydub.utils import make_chunks
from time import sleep

tones = [440, 300]

class Audio():
    def __init__(self,rate=44100):
        self.samplerate = rate
        self.channels = 1
        self.audio = None
        self.amplitude = -10

    def play(self):
        pa = pyaudio.PyAudio()
        s = pa.open(output=True,
            channels=self.channels,
            rate=self.samplerate,
            format=pyaudio.paInt16)

        for chunk in make_chunks(self.audio, 250):
            s.write(chunk._data)

    def save(self, file, codec="pcm_mulaw", format="wav"):
        self.audio.export(file, codec=codec, format=format)

    def __close__(self):
        self.s.close()
        self.pa.terminate()

    def match_target_amplitude(self, sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    def addfile(self, filename):
        sound = AudioSegment.from_file(filename).set_channels(1)
        sound = self.match_target_amplitude(sound, self.amplitude)

        if self.audio == None:
            self.audio = sound
        else:
            self.audio += sound

    def silent(self, duration):
        self.tone(1, duration, -180)

    def tone(self, frequency=440, tonelength=1000, amplitude=None):
        if amplitude == None:
            amplitude = self.amplitude
        sound = Sine(frequency, sample_rate=self.samplerate * self.channels).to_audio_segment(duration=tonelength, volume=amplitude)
        if self.audio == None:
            self.audio = sound
        else:
            self.audio += sound

alert_test=Audio(rate=48000)
alert_test.tone(tones[0], 1000)
alert_test.tone(tones[1], 1500)
alert_test.silent(1500)
alert_test.tone(tones[0], 1000)
alert_test.tone(tones[1], 1500)
alert_test.silent(5000)
alert_test.addfile("Pelmorex Test Message mp3 en.mp3")
#alert_test.play()
alert_test.save("test.wav")
