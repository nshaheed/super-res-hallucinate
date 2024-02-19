```
# split the files (not needed anymore)
ffmpeg -i pyramid_song_down_1.wav -f segment -segment_time 5.12 -c copy out%03d.wav

# run the thing
python process.py pyramid_song_down_1.wav poop 0.9
```
