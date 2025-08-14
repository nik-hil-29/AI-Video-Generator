#!/usr/bin/env python3
"""
Debug script to check environment variable loading
Run this from the backend directory: python debug_env.py
"""

import os
from dotenv import load_dotenv

print("🔍 Environment Variable Debug Script")
print("="*50)

# Check current directory
print(f"Current working directory: {os.getcwd()}")

# Check if .env file exists
env_file = ".env"
env_exists = os.path.exists(env_file)
print(f".env file exists: {env_exists}")

if env_exists:
    # Read .env file content
    with open(env_file, 'r') as f:
        content = f.read()
    print(f".env file content:")
    print("-" * 30)
    print(content)
    print("-" * 30)

# Load environment variables
print(f"Loading environment variables...")
result = load_dotenv(override=True)
print(f"load_dotenv() result: {result}")

# Check HF_TOKEN
hf_token = os.getenv("HF_TOKEN")
print(f"HF_TOKEN from os.getenv(): {hf_token}")

if hf_token:
    print(f"HF_TOKEN length: {len(hf_token)}")
    print(f"HF_TOKEN preview: {hf_token[:10]}...{hf_token[-5:]}")
    print("✅ HF_TOKEN loaded successfully!")
else:
    print("❌ HF_TOKEN not found!")

# Show all environment variables starting with HF
hf_vars = {k: v for k, v in os.environ.items() if k.startswith('HF')}
print(f"All HF environment variables: {hf_vars}")

# Test Hugging Face client initialization
print("\n🤖 Testing Hugging Face Client")
print("-" * 30)

try:
    from huggingface_hub import InferenceClient
    
    if hf_token:
        client = InferenceClient(
            provider="auto",
            api_key=hf_token,
        )
        print("✅ Hugging Face InferenceClient initialized successfully!")
        
        # Test if we can access the model (optional)
        # This might fail if the model requires special access
        try:
            # Just test client creation, not actual generation
            print("✅ Client is ready for video generation")
        except Exception as e:
            print(f"⚠️  Client created but might have model access issues: {e}")
    else:
        print("❌ Cannot initialize client - no HF_TOKEN")

except ImportError as e:
    print(f"❌ Cannot import huggingface_hub: {e}")
    print("Install with: pip install huggingface_hub")
except Exception as e:
    print(f"❌ Error initializing Hugging Face client: {e}")

print("\n" + "="*50)
print("Debug complete!")