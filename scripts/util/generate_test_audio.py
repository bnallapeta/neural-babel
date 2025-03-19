import numpy as np
import wave
import struct

def generate_sine_wave(freq, duration, sample_rate=44100):
    """Generate a sine wave at the given frequency."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * freq * t)
    return wave

def save_wav(filename, samples, sample_rate=44100):
    """Save samples as a WAV file."""
    # Normalize to 16-bit range
    samples = samples * 32767
    samples = samples.astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes (16 bits)
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            packed_sample = struct.pack('h', sample)
            wav_file.writeframes(packed_sample)

def main():
    # Generate a 3-second sine wave at 440 Hz (A4 note)
    samples = generate_sine_wave(440, 3)
    
    # Save as WAV file
    save_wav('test_audio.wav', samples)
    print("Generated test_audio.wav")

if __name__ == "__main__":
    main() 