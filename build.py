"""
Build script for MuLyCue.
Creates standalone executables using PyInstaller.
"""

import PyInstaller.__main__
import platform
import sys
from pathlib import Path
import shutil


def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_name}/")
    
    # Remove spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  Removed {spec_file}")


def get_platform_args():
    """Get platform-specific PyInstaller arguments"""
    system = platform.system()
    args = []
    
    if system == "Windows":
        args.extend([
            '--icon=assets/icon.ico',
            '--windowed',  # No console window
        ])
    elif system == "Darwin":  # macOS
        args.extend([
            '--icon=assets/icon.icns',
            '--windowed',
        ])
    else:  # Linux
        args.extend([
            '--windowed',
        ])
    
    return args


def build():
    """Build the application"""
    print(f"Building MuLyCue for {platform.system()}...")
    
    # Base arguments
    args = [
        'src/launcher.py',
        '--name=MuLyCue',
        '--onefile',
        
        # Add data files
        '--add-data=src/frontend:src/frontend',
        '--add-data=data:data',
        '--add-data=version.json:.',
        
        # Hidden imports
        '--hidden-import=uvicorn',
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.websockets',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',
        '--hidden-import=websockets',
        '--hidden-import=pygame',
        '--hidden-import=fastapi',
        '--hidden-import=pydantic',
        
        # Exclude unnecessary modules
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        
        # Clean build
        '--clean',
        '--noconfirm',
    ]
    
    # Add platform-specific arguments
    args.extend(get_platform_args())
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("\n✅ Build completed successfully!")
        print(f"   Executable location: dist/MuLyCue{'.exe' if platform.system() == 'Windows' else ''}")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)


def build_dir():
    """Build as directory (faster, for development)"""
    print(f"Building MuLyCue (directory mode) for {platform.system()}...")
    
    args = [
        'src/launcher.py',
        '--name=MuLyCue',
        '--onedir',  # Directory instead of single file
        
        # Add data files
        '--add-data=src/frontend:src/frontend',
        '--add-data=data:data',
        '--add-data=version.json:.',
        
        # Hidden imports
        '--hidden-import=uvicorn',
        '--hidden-import=websockets',
        '--hidden-import=pygame',
        
        # Clean build
        '--clean',
        '--noconfirm',
    ]
    
    args.extend(get_platform_args())
    
    try:
        PyInstaller.__main__.run(args)
        print("\n✅ Build completed successfully!")
        print(f"   Application location: dist/MuLyCue/")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Build MuLyCue executable')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts before building')
    parser.add_argument('--dir', action='store_true', help='Build as directory instead of single file')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
    
    if args.dir:
        build_dir()
    else:
        build()

