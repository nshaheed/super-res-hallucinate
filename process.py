from pydub import AudioSegment
import sys
import subprocess
import tempfile
import os
import numpy as np

import audiosr

# takes in an audio file and preps it for being super-res'd

def process_audio(base_name, input_file, model, iter_num=0, speed_factor=1.0, normalization=True):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)

    # Normalize the audio
    if normalization:
        audio = audio.normalize()

    # Change the playback speed
    audio = speed_change(audio, speed_factor)

    # Downsample
    audio = audio.set_frame_rate(4000)

    # Break into 5.12 second chunks && super-res
    # Using a tempdir to store the intermediary files
    with tempfile.TemporaryDirectory() as dir:

        # split audio into a bunch of files
        split_dur = int(5.12 * 1000) # in ms

        splits = (audio[i:i+split_dur] for i in range(0, int(audio.duration_seconds * 1000), split_dur))

        split_count = None

        # export file chunks
        for i, split in enumerate(splits):
            output_path = os.path.join(dir, f'file_{i}')
            split.export(output_path, format="wav")
            split_count = i

        entire_audio_path = os.path.join(dir, 'file_full')
        audio.export(entire_audio_path)

        # set the save path
        # TODO support save patch in config (or use hydra dirs)
        save_path = 'test'
        os.makedirs(save_path, exist_ok=True)

        # empty array to append
        full_audio = np.empty([1,1,0])

        for i in range(split_count):
        # for i in range(2):
            filepath = os.path.join(dir, f'file_{i}')

            print(f'running {filepath}')

            # run model
            # this outputs a numpy array, so I can just concat these as needed to get the full file!
            # the shape was: waveform.shape=(1, 1, 245776)
            waveform = audiosr.super_resolution(
                model, # model
                filepath, # input file
                seed=42,
                guidance_scale=3.5,
                ddim_steps=50,
                latent_t_per_second=12.8
            )

            # print(f'{waveform.shape=}')

            # append to full_audio
            full_audio = np.append(full_audio, waveform, axis=2)

        # save output to file
        # name = os.path.splitext(os.path.basename(entire_audio_path))[0] + '_AudioSR_Processed_48K'
        name = f'{base_name}-{iter_num:03}.wav'
        audiosr.save_wave(full_audio, inputpath=entire_audio_path, savepath=save_path, name=name, samplerate=48000)

        return os.path.join(save_path, name)


def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    # convert the sound with altered frame rate to a standard frame rate
    # so that regular playback programs will work right. They often only
    # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)


def calc_speed(shift, steps):
    return shift**(1.0/steps)

# call process_audio several times to slowly shift it down to the desired freq
def slow_shift(input_file, shift=0.5, steps=12):
    speed = calc_speed(shift, steps)

    # load model
    # TODO can move this out?
    # TODO device and model name are hydra configs
    model = audiosr.build_model(model_name='basic',device='cpu')

    for i in range(steps):
        # process_audio(input_file, output_file, model, speed_factor=speed, normalization=True)

        input_file = process_audio(base_name, input_file, model, iter_num=i, speed_factor=speed, normalization=True)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python processing.py input_file output_file speed_factor")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        speed_factor = float(sys.argv[3])
    except ValueError:
        print("Error: speed_factor must be a valid float")
        sys.exit(1)

    # process_audio(input_file, output_file, speed_factor=speed_factor, normalization=True)
    slow_shift(input_file, shift=0.5, steps=1)
