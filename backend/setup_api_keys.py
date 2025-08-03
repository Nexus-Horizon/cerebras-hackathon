#!/usr/bin/env python3
"""
Setup script for Qwen API configuration
This script helps you configure API keys and settings for the Qwen model
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    example_file = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not example_file.exists():
        print("❌ env.example file not found")
        return
    
    # Copy example to .env
    with open(example_file, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")

def get_user_input(prompt, default=""):
    """Get user input with default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def configure_api_keys():
    """Interactive API key configuration"""
    print("\n🔧 Qwen API Configuration Setup")
    print("=" * 40)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        create_env_file()
    
    # Read current values
    current_values = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    current_values[key] = value
    
    print("\n📝 Please provide your API configuration:")
    
    # API URL
    current_url = current_values.get("QWEN_API_URL", "http://localhost:8000/qwen/predict")
    api_url = get_user_input("Qwen API URL", current_url)
    
    # API Key
    current_key = current_values.get("QWEN_API_KEY", "")
    api_key = get_user_input("Qwen API Key (leave empty for local)", current_key)
    
    # Update .env file
    update_env_file(env_file, {
        "QWEN_API_URL": api_url,
        "QWEN_API_KEY": api_key
    })
    
    print("\n✅ Configuration saved!")
    print(f"📡 API URL: {api_url}")
    print(f"🔑 API Key: {'*' * len(api_key) if api_key else 'Not set (local mode)'}")

def update_env_file(env_file, updates):
    """Update .env file with new values"""
    lines = []
    
    # Read existing file
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update values
    updated_keys = set()
    for i, line in enumerate(lines):
        if '=' in line and not line.startswith('#'):
            key = line.split('=')[0]
            if key in updates:
                lines[i] = f"{key}={updates[key]}\n"
                updated_keys.add(key)
    
    # Add new keys
    for key, value in updates.items():
        if key not in updated_keys:
            lines.append(f"{key}={value}\n")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)

def test_configuration():
    """Test the current API configuration"""
    print("\n🧪 Testing API Configuration")
    print("=" * 40)
    
    api_url = os.getenv("QWEN_API_URL", "http://localhost:8000/qwen/predict")
    api_key = os.getenv("QWEN_API_KEY", "")
    
    print(f"📡 API URL: {api_url}")
    print(f"🔑 API Key: {'*' * len(api_key) if api_key else 'Not set'}")
    
    if api_url.startswith("http://localhost"):
        print("✅ Local API detected - no external API key needed")
    elif api_key:
        print("✅ External API with key configured")
    else:
        print("⚠️  External API detected but no API key provided")
        print("   This may cause authentication errors")

def main():
    """Main setup function"""
    print("🚀 Qwen API Setup Tool")
    print("=" * 40)
    
    try:
        create_env_file()
        configure_api_keys()
        test_configuration()
        
        print("\n🎉 Setup complete!")
        print("\n📖 Next steps:")
        print("1. Start your backend server: python run.py")
        print("2. Test the API: curl http://localhost:8000/qwen/health")
        print("3. Check the documentation: cat API_CONFIG.md")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 