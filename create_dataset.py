import glob
import sys
from videodemux import Demux
import h5py
import hashlib


def create_dataset(input_filenames, output_filename):
    h5f = h5py.File(output_filename, "w")

    for input_filename in input_filenames:
        # Split images and audio from video
        images, audio = Demux().run(input_filename)
        if images is None and audio is None:
            print("Could not load audio or video: " + input_filename)
            sys.exit(1)

        # Add to HDF5
        # Hash the filename because h5py does not allow slashes in group names.
        group_name = hashlib.md5(input_filename.encode()).hexdigest()
        h5f_group = h5f.create_group(group_name)
        h5f_group.create_dataset("images", shape=images.shape, dtype=images.dtype, data=images)
        h5f_group.create_dataset("audio", shape=audio.shape, dtype=audio.dtype, data=audio)

    h5f.close()

if __name__ == "__main__":
    input_filenames = sorted(glob.glob(sys.argv[1]))
    if len(input_filenames) == 0:
        print("No input files")
        sys.exit(1)

    create_dataset(input_filenames=input_filenames, output_filename=sys.argv[2])
