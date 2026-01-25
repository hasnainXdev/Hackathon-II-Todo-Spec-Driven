#!/usr/bin/env python3
"""
Script to run alembic migrations to fix table names from singular to plural
"""

import sys
import os
from alembic.config import Config
from alembic import command

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migrations():
    """Run the alembic migrations to fix table names"""
    try:
        print("Running alembic migrations to fix table names...")
        
        # Change to the backend directory
        os.chdir('/mnt/d/it-course/hackathons/hackathon-II-todo-spec-driven/phase-3/backend')
        
        # Create alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        
        print("✓ Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migrations()
    if success:
        print("\n🎉 Database tables have been updated successfully!")
    else:
        print("\n❌ Migration failed.")
        sys.exit(1)