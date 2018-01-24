# videodemux
Python module to split videos into raw frames and audio samples and create an HDF5 dataset

Usage:

```
from videodemux import Demux
images, audio = Demux().run(input_filename)
```

```images``` is a numpy array containing raw 8-bit RGB video frames.  ```audio``` is a numpy array of signed 16-bit stereo PCM samples.
