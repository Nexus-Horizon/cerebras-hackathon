#!/usr/bin/env python3
"""
Setup script for Cerebras Qwen configuration
This script helps you configure Cerebras API keys and settings
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

def get_user_input(prompt, default="", password=False):
    """Get user input with default value"""
    if password:
        import getpass
        user_input = getpass.getpass(f"{prompt}: ").strip()
        return user_input if user_input else default
    else:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()

def configure_cerebras():
    """Interactive Cerebras configuration"""
    print("\n🔧 Cerebras Qwen Configuration Setup")
    print("=" * 50)
    
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
    
    print("\n📝 Please provide your Cerebras configuration:")
    
    # Enable Cerebras
    current_enabled = current_values.get("USE_CEREBRAS_QWEN", "false")
    enable_cerebras = get_user_input("Enable Cerebras Qwen (true/false)", current_enabled)
    
    # API URL
    current_url = current_values.get("CEREBRAS_API_URL", "https://api.cerebras.com/v1/chat/completions")
    api_url = get_user_input("Cerebras API URL", current_url)
    
    # API Key
    current_key = current_values.get("CEREBRAS_API_KEY", "")
    api_key = get_user_input("Cerebras API Key (leave empty to skip)", current_key, password=True)
    
    # Model Name
    current_model = current_values.get("CEREBRAS_MODEL_NAME", "qwen-7b")
    model_name = get_user_input("Cerebras Model Name", current_model)
    
    # Model Parameters
    current_max_tokens = current_values.get("CEREBRAS_MAX_TOKENS", "100")
    max_tokens = get_user_input("Max Tokens", current_max_tokens)
    
    current_temperature = current_values.get("CEREBRAS_TEMPERATURE", "0.7")
    temperature = get_user_input("Temperature", current_temperature)
    
    current_timeout = current_values.get("CEREBRAS_TIMEOUT", "30")
    timeout = get_user_input("Timeout (seconds)", current_timeout)
    
    # Debug Mode
    current_debug = current_values.get("DEBUG_CEREBRAS", "false")
    debug_mode = get_user_input("Enable Debug Mode (true/false)", current_debug)
    
    # Update .env file
    updates = {
        "USE_CEREBRAS_QWEN": enable_cerebras,
        "CEREBRAS_API_URL": api_url,
        "CEREBRAS_API_KEY": api_key,
        "CEREBRAS_MODEL_NAME": model_name,
        "CEREBRAS_MAX_TOKENS": max_tokens,
        "CEREBRAS_TEMPERATURE": temperature,
        "CEREBRAS_TIMEOUT": timeout,
        "DEBUG_CEREBRAS": debug_mode
    }
    
    update_env_file(env_file, updates)
    
    print("\n✅ Cerebras configuration saved!")
    print(f"🔧 Enabled: {enable_cerebras}")
    print(f"📡 API URL: {api_url}")
    print(f"🤖 Model: {model_name}")
    print(f"🔑 API Key: {'*' * len(api_key) if api_key else 'Not set'}")
    print(f"⚙️  Max Tokens: {max_tokens}")
    print(f"🌡️  Temperature: {temperature}")
    print(f"⏱️  Timeout: {timeout}s")
    print(f"🐛 Debug Mode: {debug_mode}")

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

def test_cerebras_connection():
    """Test the Cerebras connection"""
    print("\n🧪 Testing Cerebras Connection")
    print("=" * 40)
    
    # Import after configuration
    try:
        from app.routers.cerebras_qwen import call_cerebras_qwen, get_cerebras_config
        
        config = get_cerebras_config()
        print(f"📡 API URL: {config.api_url}")
        print(f"🤖 Model: {config.model_name}")
        print(f"🔑 API Key: {'*' * len(config.api_key) if config.api_key else 'Not set'}")
        
        if not config.api_key:
            print("⚠️  No API key provided - connection test skipped")
            return
        
        # Test with a simple prompt
        print("\n🔄 Testing with simple prompt...")
        test_prompt = "Hello, this is a test."
        
        try:
            response = call_cerebras_qwen(test_prompt)
            if response.startswith("Error:"):
                print(f"❌ Connection failed: {response}")
            else:
                print(f"✅ Connection successful!")
                print(f"📝 Response: {response[:100]}...")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            
    except ImportError as e:
        print(f"❌ Could not import Cerebras module: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_next_steps():
    """Show next steps for the user"""
    print("\n📖 Next Steps:")
    print("1. Start your backend server: python run.py")
    print("2. Test the integration with a sample request")
    print("3. Check the logs for any errors")
    print("4. Monitor performance and costs")
    print("\n📚 Documentation:")
    print("- Cerebras Guide: cat CEREBRAS_QWEN_GUIDE.md")
    print("- API Config: cat API_CONFIG.md")
    print("- Environment: cat .env")

def main():
    """Main setup function"""
    print("🚀 Cerebras Qwen Setup Tool")
    print("=" * 50)
    
    try:
        create_env_file()
        configure_cerebras()
        test_cerebras_connection()
        show_next_steps()
        
        print("\n🎉 Cerebras setup complete!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 