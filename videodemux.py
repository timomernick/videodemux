import glob
import os
import sys
import subprocess
import tempfile
import numpy as np
import scipy
import scipy.misc
import h5py
from scipy.io import wavfile


class Demux(object):
    def __init__(self, image_height=64, image_width=64, num_components=3, output_framerate=15):
        self.image_height = image_height
        self.image_width = image_width
        self.num_components = num_components
        self.output_framerate = output_framerate
        self.output_dir = None

    def images_path(self):
        return self.output_dir + "/images"

    def audio_path(self):
        return self.output_dir + "/audio"

    def run(self, filename):
        print("Splitting: " + filename)

        self.output_dir = tempfile.mkdtemp()

        images_dir = self.images_path()
        os.mkdir(images_dir)

        audio_dir = self.audio_path()
        os.mkdir(audio_dir)

        images = self.split_frames(filename, images_dir)
        audio = self.split_audio(filename, audio_dir)

        return images, audio

    def run_ffmpeg(self, ffmpeg_args):
        #print("    " + " ".join(ffmpeg_args))
        process = subprocess.Popen(ffmpeg_args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process_out, process_err = process.communicate()
        #print(process_out)
        #print(process_err)

        process.wait()

    def split_frames(self, filename, images_dir):
        #print("  Splitting frames...")

        scale_string = str(self.image_width) + ":" + str(self.image_height)
        ffmpeg_args = ["ffmpeg",
                        "-i", filename,
                        "-vf", "scale=" + scale_string,
                        "-r", str(self.output_framerate),
                        "-f", "image2",
                        images_dir + "/%07d.png"]
        self.run_ffmpeg(ffmpeg_args=ffmpeg_args)

        return self.gather_frames(images_dir)

    def gather_frames(self, images_dir):
        frame_filenames = sorted(glob.glob(images_dir + "/*.png"))
        num_frames = len(frame_filenames)
        frames = np.zeros(shape=[num_frames, self.num_components, self.image_height, self.image_width],
                          dtype=np.uint8)

        for frame_idx in range(num_frames):
            frame_filename = frame_filenames[frame_idx]
            frame = scipy.misc.imread(frame_filename)
            frame = frame.transpose(2, 0, 1)
            frames[frame_idx] = frame
            #print(frame_filename, frame.dtype, frame.shape)

        return frames

    def split_audio(self, filename, audio_dir):
        #print("  Splitting audio...")

        output_filename = audio_dir + "/audio.wav"
        ffmpeg_args = ["ffmpeg",
                        "-i", filename,
                        "-vn",
                        "-acodec", "pcm_s16le",
                        "-ar", "44100",
                        "-ac", "2",
                       output_filename]
        self.run_ffmpeg(ffmpeg_args=ffmpeg_args)

        return self.gather_audio(filename, output_filename)

    def gather_audio(self, video_filename, audio_filename):
        try:
            rate, wav = wavfile.read(audio_filename)
            return wav
        except:
            print("Could not load audio: " + video_filename)
            sys.exit(1)
