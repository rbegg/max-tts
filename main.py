import asyncio
import argparse
import wave
from pathlib import Path

from wyoming.client import AsyncClient
from wyoming.tts import Synthesize
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.event import Event


async def test_tts_service(uri: str, text: str, output_path: str):
    """
    Connects to a Wyoming TTS service using the wyoming library,
    sends text for synthesis, and saves the received audio to a WAV file.

    Args:
        uri: The client URI of the Wyoming service (e.g., tcp://localhost:10300).
        text: The text to synthesize.
        output_path: The path to save the output WAV file.
    """
    print(f"Connecting to {uri}...")
    try:
        async with AsyncClient.from_uri(uri) as client:
            print("Connection established.")

            # 1. Send synthesize request
            synthesize_event = Synthesize(text=text)
            await client.write_event(synthesize_event.event())
            print(f"Sent synthesize request for: '{text}'")

            # 2. Receive audio
            audio_chunks = []
            audio_params = {}
            wav_file = None

            while True:
                event = await client.read_event()
                if event is None:
                    print("Connection closed by server.")
                    break

                print(f"Received event: {event.type}")

                if AudioStart.is_type(event.type):
                    start_event = AudioStart.from_event(event)
                    audio_params = {
                        "nchannels": start_event.channels,
                        "sampwidth": start_event.width,
                        "framerate": start_event.rate,
                    }
                    print(f"Audio stream started with params: {audio_params}")

                    # Open WAV file for writing
                    wav_file = wave.open(output_path, "wb")
                    wav_file.setnchannels(audio_params["nchannels"])
                    wav_file.setsampwidth(audio_params["sampwidth"])
                    wav_file.setframerate(audio_params["framerate"])

                elif AudioChunk.is_type(event.type):
                    chunk_event = AudioChunk.from_event(event)
                    print(f"Received audio chunk of size {len(chunk_event.audio)}")
                    if wav_file is not None:
                        wav_file.writeframes(chunk_event.audio)

                elif AudioStop.is_type(event.type):
                    print("Audio stream finished.")
                    break

                elif Event.is_type(event.type, "error"):
                    print(f"Received error from server: {event.data.get('text')}")
                    break

            if wav_file is not None:
                wav_file.close()
                print(f"Successfully saved WAV file to {output_path}")
            else:
                print("No audio data was received.")


    except ConnectionRefusedError:
        print(f"Connection to {uri} refused. Is the service running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wyoming TTS Test Client")
    parser.add_argument(
        "--uri",
        default="tcp://localhost:10200",
        help="Client URI of the Wyoming TTS service",
    )
    parser.add_argument(
        "--text",
        default="Hello from the Python test client.",
        help="Text to synthesize",
    )
    parser.add_argument(
        "--output",
        default="output.wav",
        help="Path to save the output WAV file",
    )
    args = parser.parse_args()

    # Ensure the output directory exists
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    asyncio.run(test_tts_service(args.uri, args.text, args.output))

