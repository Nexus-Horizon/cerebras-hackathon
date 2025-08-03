#!/usr/bin/env python3
"""
Script to set up environment variables for the backend
"""
import os
import shutil

def setup_env():
    """Copy env.example to .env if .env doesn't exist"""
    env_example_path = "env.example"
    env_path = ".env"
    
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            shutil.copy(env_example_path, env_path)
            print(f"Created {env_path} from {env_example_path}")
            print("Please edit .env file to set your actual API keys and configuration")
        else:
            print(f"Error: {env_example_path} not found")
    else:
        print(f"{env_path} already exists")

if __name__ == "__main__":
    setup_env() 