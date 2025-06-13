#!/usr/bin/env python3
"""
Configuration settings for Inquiro RAG System

This module centralizes all file paths and directory configurations
to support the move to C:\\inquiro for data storage.
"""

import os
from pathlib import Path

# Base directory for all Inquiro data storage
INQUIRO_BASE_DIR = Path("C:/inquiro")

# Data storage directories
DATA_PATH = str(INQUIRO_BASE_DIR / "data")
FAISS_PATH = str(INQUIRO_BASE_DIR / "database" / "faiss_index")

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(FAISS_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(FAISS_PATH), exist_ok=True)

# Initialize directories on import
ensure_directories()

# Legacy support - check if old directories exist and offer migration
def check_legacy_data():
    """Check for data in old locations and suggest migration."""
    old_data_path = "data"
    old_faiss_path = "faiss_index"
    
    legacy_data_exists = os.path.exists(old_data_path)
    legacy_faiss_exists = os.path.exists(old_faiss_path)
    
    return {
        "data_exists": legacy_data_exists,
        "faiss_exists": legacy_faiss_exists,
        "old_data_path": old_data_path,
        "old_faiss_path": old_faiss_path
    }

def migrate_legacy_data():
    """Migrate data from old locations to new C:\\inquiro structure."""
    import shutil
    
    legacy_info = check_legacy_data()
    migrated_files = []
    
    # Migrate data files
    if legacy_info["data_exists"]:
        old_data_path = legacy_info["old_data_path"]
        for file_name in os.listdir(old_data_path):
            if file_name.endswith(('.pdf', '.txt', '.md')):
                old_file = os.path.join(old_data_path, file_name)
                new_file = os.path.join(DATA_PATH, file_name)
                
                if not os.path.exists(new_file):
                    shutil.copy2(old_file, new_file)
                    migrated_files.append(f"Data: {file_name}")
    
    # Migrate FAISS database
    if legacy_info["faiss_exists"]:
        old_faiss_path = legacy_info["old_faiss_path"]
        if os.path.exists(old_faiss_path) and os.listdir(old_faiss_path):
            # Copy entire FAISS directory
            if not os.path.exists(FAISS_PATH):
                shutil.copytree(old_faiss_path, FAISS_PATH)
                migrated_files.append("Database: FAISS index")
            else:
                # Copy individual files if directory exists
                for file_name in os.listdir(old_faiss_path):
                    old_file = os.path.join(old_faiss_path, file_name)
                    new_file = os.path.join(FAISS_PATH, file_name)
                    if not os.path.exists(new_file):
                        shutil.copy2(old_file, new_file)
                        migrated_files.append(f"Database: {file_name}")
    
    return migrated_files

if __name__ == "__main__":
    # When run directly, perform migration and show status
    print("🔧 Inquiro Configuration & Migration Tool")
    print("=" * 50)
    
    print(f"✅ Base directory: {INQUIRO_BASE_DIR}")
    print(f"✅ Data directory: {DATA_PATH}")
    print(f"✅ Database directory: {FAISS_PATH}")
    
    legacy_info = check_legacy_data()
    
    if legacy_info["data_exists"] or legacy_info["faiss_exists"]:
        print("\n📦 Legacy data found:")
        if legacy_info["data_exists"]:
            print(f"   • Data files in: {legacy_info['old_data_path']}")
        if legacy_info["faiss_exists"]:
            print(f"   • Database in: {legacy_info['old_faiss_path']}")
        
        print("\n🚚 Migrating to new location...")
        migrated = migrate_legacy_data()
        
        if migrated:
            print("✅ Migration successful:")
            for item in migrated:
                print(f"   • {item}")
        else:
            print("ℹ️ No new files to migrate (files may already exist in new location)")
    else:
        print("\nℹ️ No legacy data found - starting fresh")
    
    print(f"\n🎉 Inquiro is now configured to use: {INQUIRO_BASE_DIR}")
