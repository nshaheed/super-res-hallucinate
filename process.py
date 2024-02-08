from pydub import AudioSegment
import sys
import subprocess

# takes in an audio file and preps it for being super-res'd

def process_audio(input_file, output_file, normalization=True, speed_factor=1.0):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)

    # Normalize the audio
    if normalization:
        audio = audio.normalize()

    # Change the playback speed
    audio = speed_change(audio, speed_factor)

    # Downsample
    audio = audio.set_frame_rate(4000)

    # Break into 5.12 second chunks

    # Export all chunks


    # Export the modified audio to a new file
    audio.export(output_file, format="wav")
    print(f'Audio processed successfully. Saved as {output_file}')    

    # Call audiosr
    # command = "audiosr -i .\\pyramid_song_down_1.wav"
    command = "audiosr -i out000.wav"    

    try:
        subprocess.run(command, shell=True, check=True)
        # subprocess.run(["powershell", "-Command", command], check=True)
    except subprocess.CalledProcessError as e:
        print("Error:", e)

    # Stitch together results

    # ...I'm missing something here



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

    process_audio(input_file, output_file, normalization=True, speed_factor=speed_factor)
