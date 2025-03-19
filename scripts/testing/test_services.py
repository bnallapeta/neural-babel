#!/usr/bin/env python3
import asyncio
import httpx
import json

async def check_service_health(service_name, url):
    """Test a service endpoint and print the response."""
    health_url = f"{url}/health"
    
    print(f"\nTesting {service_name} at {health_url}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(health_url, timeout=5.0)
            
        print(f"Status code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        except:
            print(f"Response (raw): {response.text}")
            return response.status_code == 200
    except Exception as e:
        print(f"Error connecting to {service_name}: {str(e)}")
        return False

async def main():
    """Test all services."""
    print("=== Testing NeuralBabel Service Connections ===")
    
    services = [
        ("ASR Service", "http://localhost:8666"),
        ("Translation Service", "http://localhost:8777"),
        ("TTS Service", "http://localhost:8888"),
        ("NeuralBabel", "http://localhost:8005")
    ]
    
    results = {}
    for name, url in services:
        results[name] = await check_service_health(name, url)
    
    print("\n=== Summary ===")
    for name, success in results.items():
        status = "✅ OK" if success else "❌ FAILED"
        print(f"{name}: {status}")

if __name__ == "__main__":
    asyncio.run(main()) 