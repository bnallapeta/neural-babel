# NeuralBabel Manual Testing

This directory contains files and scripts for manually testing the NeuralBabel pipeline. It provides detailed logs and outputs from each stage of the pipeline to help verify that the translation is working correctly.

## Files

- `input.wav`: Input audio file in English for testing the pipeline
- `transcription.txt`: Text output from the ASR service (speech-to-text)
- `translation.txt`: Translated text from the Translation service (English to French, or other target language)
- `translated.wav`: Output audio file from the TTS service (French speech)

## Scripts

- `run_test.sh`: Shell script to run the detailed test pipeline
- `run_detailed_test.py`: Python script that tests each component of the pipeline and logs the intermediate results
- `set_test_input.sh`: Script to set a new input audio file for testing

## How to Run

1. Ensure all three services are running:
   - ASR Service on port 8666
   - Translation Service on port 8777
   - TTS Service on port 8888

2. (Optional) Set a new input audio file:
   ```bash
   ./set_test_input.sh /path/to/your/audio.wav
   ```

3. Run the test script:
   ```bash
   ./run_test.sh
   ```

4. Check the output files to verify the translation pipeline:
   - `transcription.txt`: Contains the original text transcribed from the input audio
   - `translation.txt`: Contains the translated text
   - `translated.wav`: Contains the synthesized speech of the translated text

## Troubleshooting

- If ASR returns an empty transcription, the script will use a fallback test message
- If any service is not running or returns an error, the script will report the issue 