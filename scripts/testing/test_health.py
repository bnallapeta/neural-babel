#!/usr/bin/env python

import asyncio
import httpx
import json
import traceback

async def check_health(service_url, service_name):
    """Check health of a service"""
    health_url = f"{service_url}/health"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(health_url, timeout=5.0)
        
        print(f"{service_name} Health Status Code: {response.status_code}")
        print(f"{service_name} Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"{service_name} Health Check Error: {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("Testing Health Endpoints...")
    
    services = {
        "ASR": "http://localhost:8001",
        "Translation": "http://localhost:8002",
        "TTS": "http://localhost:8003",
        "NeuralBabel": "http://localhost:8005"
    }
    
    for name, url in services.items():
        is_healthy = await check_health(url, name)
        print(f"{name} is {'healthy' if is_healthy else 'unhealthy'}\n")
    
    # Try a direct curl-like request to the NeuralBabel health endpoint
    print("Trying direct request to NeuralBabel health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8005/health", timeout=5.0, headers={"User-Agent": "test-script"})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        health_data = response.json()
        print("Neural Babel Health Detail:")
        print(json.dumps(health_data, indent=2))
    except Exception as e:
        print(f"Error getting Neural Babel health: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 