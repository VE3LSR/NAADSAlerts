#!/usr/bin/python3

import sys,gi,time
gi.require_version('Gst', '1.0')

ToneA = 440
ToneB = 300

from gi.repository import Gst

Gst.init(None)

class Main:
    def __init__(self):
        print("INIT")
        self.pipeline = Gst.Pipeline.new('test-pipeline')
        self.bus = self.pipeline.get_bus()
        # Create a Tee to connect too
        self.tee = Gst.ElementFactory.make("tee", "audiotee")
        self.pipeline.add(self.tee)
        ret = self.pipeline.set_state(Gst.State.PLAYING)

    def link(self, element1, element2):
        element1.link(element2)

    def addAudioSink(self):
        self.audiosink = Gst.ElementFactory.make("autoaudiosink", "audiosink")
        self.pipeline.add(self.audiosink)
        self.audiosink.sync_state_with_parent();
        self.link(self.tee, self.audiosink)

    def addFileSink(self):
        self.encoder = Gst.ElementFactory.make('lamemp3enc', 'encoder')
        self.pipeline.add(self.encoder)
        self.encoder.sync_state_with_parent();
        
        self.filesink = Gst.ElementFactory.make("filesink", "filesink")
        self.filesink.set_property('location', 'test.mp3')
        self.pipeline.add(self.filesink)
        self.filesink.sync_state_with_parent();

        self.link(self.tee, self.encoder)
        self.link(self.encoder, self.filesink)

    def probe_block(self, pad, buf):
        print("blocked")
        return True

    def PlayTones(self, tone1, tone2, tone1time, tone2time):
        print("Playing Tones")

        tonesrc = Gst.ElementFactory.make("audiotestsrc", "Tone")
        tonesrc.set_property('volume', .1)
        tonesrc.set_property('is-live', True)

        self.pipeline.add(tonesrc)
        self.link(tonesrc,self.tee)

        # Start Playing Tone 1
        print("Tone 1")
        tonesrc.set_property('freq', tone1) # Change to first freq
        ret = tonesrc.set_state(Gst.State.PLAYING)

        time.sleep(tone1time) # Play tone 1 for 2 seconds

        # Start playing tone 2
        print("Tone 2")
        tonesrc.set_property('freq', tone2) # Change to second freq
        time.sleep(tone2time) # Play tone 2 for 2 seconds

        # Deconstruct our pipeline
        tonesrc.get_static_pad('src').add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.probe_block)
        tonesrc.unlink(self.tee)
        tonesrc.set_state(Gst.State.NULL)
        self.pipeline.remove(tonesrc)
#        self.pipeline.set_state(Gst.State.READY)
        print("Finished Tones")

    def PlayFile(self, file):

        print("Playing " + file)
        filesrc = Gst.ElementFactory.make("filesrc", "filesrc")
        filesrc.set_property("location", file)
        self.pipeline.add(filesrc)

        decodesrc = Gst.ElementFactory.make("mad", "decode")
        self.pipeline.add(decodesrc)

        self.link(filesrc,decodesrc)
        self.link(decodesrc,self.tee)

        decodesrc.sync_state_with_parent();
#        filesrc.sync_state_with_parent();

        filesrc.set_state(Gst.State.PLAYING)

        msg = self.bus.timed_pop_filtered(
               Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

        decodesrc.get_static_pad('src').add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.probe_block)
        filesrc.get_static_pad('src').add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.probe_block)
        self.pipeline.unlink(decodesrc)
        self.pipeline.unlink(filesrc)
        self.pipeline.remove(decodesrc)
        self.pipeline.remove(filesrc)

    def End(self):
        ret = self.pipeline.set_state(Gst.State.NULL)


start=Main()

#start.addAudioSink()
start.addFileSink()

# I can play PlayTones twice, with no issues,
# However the moment I change from PlayTones to PlayFile (or the reverse) it produces no audio
# Except the debug log shows it playing sounds

start.PlayTones(ToneA, ToneB, .5, .5)
time.sleep(1)
start.PlayTones(ToneA, ToneB, .5, .5)
time.sleep(1)
start.PlayFile("Pelmorex Test Message mp3 en.mp3")
time.sleep(2)
#start.PlayFile("/home/Repos/CoolAcid/NAAD/Pelmorex Test Message mp3 en.mp3")
#start.PlayTones(ToneA, ToneB, .5, .5)
#start.PlayTones(ToneA, ToneB, .5, .5)
start.End()
