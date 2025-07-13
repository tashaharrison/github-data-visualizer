#!/usr/bin/env python3
"""
Setup script for GitHub PR Analytics AI Agent.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            os.system('cp env.example .env')
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your API keys and configuration")
        else:
            print("❌ env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import langchain
        import openai
        import pandas
        import matplotlib
        import aiohttp
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_github_token():
    """Test GitHub token configuration."""
    from config.settings import settings
    try:
        import aiohttp
        import asyncio
        
        async def test():
            headers = {
                "Authorization": f"token {settings.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.github.com/user", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        print(f"✅ GitHub token valid - authenticated as: {user_data.get('login', 'Unknown')}")
                        return True
                    else:
                        print(f"❌ GitHub token invalid - status: {response.status}")
                        return False
        
        return asyncio.run(test())
    except Exception as e:
        print(f"❌ Error testing GitHub token: {e}")
        return False

def test_openai_key():
    """Test OpenAI API key."""
    from config.settings import settings
    try:
        import openai
        client = openai.OpenAI(api_key=settings.openai_api_key)
        response = client.models.list()
        print("✅ OpenAI API key valid")
        return True
    except Exception as e:
        print(f"❌ OpenAI API key invalid: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up GitHub PR Analytics AI Agent")
    print("=" * 50)
    
    # Create .env file
    if not create_env_file():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Test API keys (only if .env is configured)
    if os.path.exists('.env'):
        print("\n🔑 Testing API keys...")
        
        # Import settings after .env is created
        sys.path.append(str(Path(__file__).parent))
        from config.settings import settings
        
        github_ok = test_github_token()
        openai_ok = test_openai_key()
        
        if github_ok and openai_ok:
            print("\n✅ Setup complete! You can now run:")
            print("   python main.py")
        else:
            print("\n❌ Please fix the API key issues above before running the agent")
    else:
        print("\n📝 Please configure your .env file and run setup again")

if __name__ == "__main__":
    main() 