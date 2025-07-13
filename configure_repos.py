#!/usr/bin/env python3
"""
Helper script to configure multiple repositories for analysis.
"""

import json
import os
from pathlib import Path


def create_repo_config():
    """Interactive script to create repository configuration."""
    print("🔧 GitHub PR Analytics - Repository Configuration")
    print("=" * 50)
    
    repos = []
    
    while True:
        print(f"\nRepository {len(repos) + 1}:")
        owner = input("  Owner/Organization: ").strip()
        if not owner:
            break
            
        name = input("  Repository Name: ").strip()
        if not name:
            print("  ❌ Repository name is required")
            continue
            
        display_name = input("  Display Name (optional, press Enter for default): ").strip()
        if not display_name:
            display_name = f"{owner}/{name}"
        
        repos.append({
            "owner": owner,
            "name": name,
            "display_name": display_name
        })
        
        print(f"  ✅ Added: {display_name}")
        
        more = input("\nAdd another repository? (y/n): ").strip().lower()
        if more != 'y':
            break
    
    if not repos:
        print("\n❌ No repositories configured")
        return
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating .env file from template...")
        if Path("env.example").exists():
            os.system("cp env.example .env")
            print("✅ Created .env file")
        else:
            print("❌ env.example not found")
            return
    
    # Update .env file with repository configuration
    repos_json = json.dumps(repos)
    
    # Read current .env file
    with open(".env", "r") as f:
        env_content = f.read()
    
    # Update or add REPOSITORIES line
    if "REPOSITORIES=" in env_content:
        # Replace existing line
        lines = env_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("REPOSITORIES="):
                lines[i] = f"REPOSITORIES={repos_json}"
                break
        env_content = "\n".join(lines)
    else:
        # Add new line
        env_content += f"\nREPOSITORIES={repos_json}\n"
    
    # Write updated .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print(f"\n✅ Configured {len(repos)} repositories:")
    for repo in repos:
        print(f"  - {repo['display_name']}")
    
    print(f"\n📝 Repository configuration saved to .env file")
    print(f"🔧 You can now run: python main.py")


def show_current_config():
    """Show current repository configuration."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found")
        return
    
    with open(".env", "r") as f:
        content = f.read()
    
    print("📋 Current Configuration:")
    print("=" * 30)
    
    # Extract repository info
    for line in content.split("\n"):
        if line.startswith("REPO_OWNER="):
            owner = line.split("=", 1)[1]
            print(f"Single Repo Owner: {owner}")
        elif line.startswith("REPO_NAME="):
            name = line.split("=", 1)[1]
            print(f"Single Repo Name: {name}")
        elif line.startswith("REPOSITORIES="):
            repos_json = line.split("=", 1)[1]
            try:
                repos = json.loads(repos_json)
                print(f"Multi-Repo Configuration: {len(repos)} repositories")
                for repo in repos:
                    display_name = repo.get("display_name", f"{repo['owner']}/{repo['name']}")
                    print(f"  - {display_name}")
            except json.JSONDecodeError:
                print("  ❌ Invalid JSON format")


def main():
    """Main function."""
    print("🚀 GitHub PR Analytics - Repository Configuration")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Configure multiple repositories")
        print("2. Show current configuration")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            create_repo_config()
        elif choice == "2":
            show_current_config()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main() 