#!/usr/bin/env python3
"""
Test script for Cerebras API connectivity
This script helps diagnose connectivity issues with the Cerebras API
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dns_resolution(domain: str) -> bool:
    """Test DNS resolution for a domain"""
    try:
        import socket
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def test_http_connectivity(url: str, timeout: int = 5) -> dict:
    """Test HTTP connectivity to a URL"""
    result = {
        "url": url,
        "dns_resolution": False,
        "http_connectivity": False,
        "status_code": None,
        "error": None
    }
    
    # Extract domain from URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Test DNS resolution
    result["dns_resolution"] = test_dns_resolution(domain)
    
    if not result["dns_resolution"]:
        result["error"] = f"DNS resolution failed for {domain}"
        return result
    
    # Test HTTP connectivity
    try:
        response = requests.head(url, timeout=timeout)
        result["http_connectivity"] = True
        result["status_code"] = response.status_code
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection error: {str(e)}"
    except requests.exceptions.Timeout as e:
        result["error"] = f"Timeout: {str(e)}"
    except Exception as e:
        result["error"] = f"Error: {str(e)}"
    
    return result

def main():
    """Main test function"""
    print("🔍 Cerebras API Connectivity Test")
    print("=" * 50)
    
    # Get configuration
    api_url = os.getenv("CEREBRAS_API_URL", "https://api.cerebras.com/v1/chat/completions")
    api_key = os.getenv("CEREBRAS_API_KEY")
    debug_mode = os.getenv("DEBUG_CEREBRAS", "false").lower() == "true"
    
    print(f"📋 Configuration:")
    print(f"   API URL: {api_url}")
    print(f"   API Key: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"   Debug Mode: {'✅ Enabled' if debug_mode else '❌ Disabled'}")
    print()
    
    # Test URLs to check
    test_urls = [
        "https://api.cerebras.com/v1/chat/completions",
        "https://api.cerebras.com/v1/completions",
        "https://api.cerebras.com/chat/completions",
        "https://api.cerebras.com/completions",
        "https://cerebras-api.com/v1/chat/completions",
        "https://cerebras-api.com/v1/completions"
    ]
    
    print("🌐 Testing API Endpoints:")
    print("-" * 50)
    
    working_endpoints = []
    
    for url in test_urls:
        result = test_http_connectivity(url)
        
        status_icon = "✅" if result["http_connectivity"] else "❌"
        print(f"{status_icon} {url}")
        
        if result["dns_resolution"]:
            print(f"   DNS: ✅ Resolved")
        else:
            print(f"   DNS: ❌ Failed")
        
        if result["http_connectivity"]:
            print(f"   HTTP: ✅ Connected (Status: {result['status_code']})")
            working_endpoints.append(url)
        else:
            print(f"   HTTP: ❌ Failed - {result['error']}")
        
        print()
    
    # Summary
    print("📊 Summary:")
    print("-" * 50)
    
    if working_endpoints:
        print(f"✅ Found {len(working_endpoints)} working endpoint(s):")
        for endpoint in working_endpoints:
            print(f"   • {endpoint}")
    else:
        print("❌ No working endpoints found")
        print()
        print("🔧 Troubleshooting suggestions:")
        print("   1. Check your internet connection")
        print("   2. Verify the API endpoint URL")
        print("   3. Check if you're behind a firewall/proxy")
        print("   4. Try using a VPN if needed")
        print("   5. Contact Cerebras support for correct endpoints")
    
    print()
    
    # Test with actual API call if we have a working endpoint
    if working_endpoints and api_key:
        print("🧪 Testing actual API call...")
        try:
            from app.routers.cerebras_qwen import call_cerebras_qwen
            
            # Test with a simple prompt
            test_prompt = "Hello, this is a test message."
            result = call_cerebras_qwen(test_prompt)
            
            if result.startswith("Error:"):
                print(f"❌ API call failed: {result}")
            else:
                print(f"✅ API call successful: {result[:100]}...")
                
        except Exception as e:
            print(f"❌ Error testing API call: {str(e)}")
    
    print()
    print("🏁 Test completed!")

if __name__ == "__main__":
    main() 