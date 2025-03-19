#!/usr/bin/env python
import requests
import json
import time
import os
import argparse

def test_health(base_url):
    """Test the health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{base_url}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_ready(base_url):
    """Test the readiness endpoint."""
    print("\n=== Testing Readiness Endpoint ===")
    response = requests.get(f"{base_url}/ready")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_live(base_url):
    """Test the liveness endpoint."""
    print("\n=== Testing Liveness Endpoint ===")
    response = requests.get(f"{base_url}/live")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_config(base_url):
    """Test the configuration endpoint."""
    print("\n=== Testing Configuration Endpoint ===")
    response = requests.get(f"{base_url}/config")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_languages(base_url):
    """Test the languages endpoint."""
    print("\n=== Testing Languages Endpoint ===")
    response = requests.get(f"{base_url}/languages")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_translate_form(base_url, audio_file):
    """Test the translation endpoint with form data."""
    print("\n=== Testing Translation Endpoint (Form) ===")
    
    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"Error: Audio file {audio_file} not found.")
        return False
    
    # Prepare form data
    files = {
        'audio': open(audio_file, 'rb')
    }
    data = {
        'source_lang': 'en',
        'target_lang': 'fr',
        'audio_format': 'wav',
        'voice': 'default'
    }
    
    # Make request
    start_time = time.time()
    response = requests.post(f"{base_url}/translate", files=files, data=data)
    duration = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Duration: {duration:.2f} seconds")
    
    if response.status_code == 200:
        # Save the response audio
        output_file = "response_audio.wav"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Response audio saved to {output_file}")
        
        # Print headers
        print("Headers:")
        for key, value in response.headers.items():
            if key.startswith("X-"):
                print(f"  {key}: {value}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def main():
    parser = argparse.ArgumentParser(description="Test the NeuralBabel API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the NeuralBabel API")
    parser.add_argument("--audio", default="test_audio.wav", help="Audio file to use for testing")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--health", action="store_true", help="Test health endpoint")
    parser.add_argument("--ready", action="store_true", help="Test readiness endpoint")
    parser.add_argument("--live", action="store_true", help="Test liveness endpoint")
    parser.add_argument("--config", action="store_true", help="Test configuration endpoint")
    parser.add_argument("--languages", action="store_true", help="Test languages endpoint")
    parser.add_argument("--translate", action="store_true", help="Test translation endpoint")
    
    args = parser.parse_args()
    
    # If no specific tests are selected, run all tests
    run_all = args.all or not (args.health or args.ready or args.live or args.config or args.languages or args.translate)
    
    results = {}
    
    if args.health or run_all:
        results["health"] = test_health(args.url)
    
    if args.ready or run_all:
        results["ready"] = test_ready(args.url)
    
    if args.live or run_all:
        results["live"] = test_live(args.url)
    
    if args.config or run_all:
        results["config"] = test_config(args.url)
    
    if args.languages or run_all:
        results["languages"] = test_languages(args.url)
    
    if args.translate or run_all:
        results["translate"] = test_translate_form(args.url, args.audio)
    
    # Print summary
    print("\n=== Test Summary ===")
    all_passed = True
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test}: {status}")
        all_passed = all_passed and passed
    
    print(f"\nOverall: {'PASSED' if all_passed else 'FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main()) 