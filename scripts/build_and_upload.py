#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Clean up build directories"""
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for dir_pattern in dirs_to_clean:
        for path in Path('.').glob(dir_pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    print("✓ Cleaned build directories")

def build_package():
    """Build the package"""
    subprocess.run(['python', '-m', 'build'], check=True)
    print("✓ Built package")

def upload_to_pypi():
    """Upload to PyPI using twine and project's .pypirc"""
    pypirc_path = Path('.pypirc').absolute()
    if not pypirc_path.exists():
        raise FileNotFoundError("Could not find .pypirc in project directory")
    
    subprocess.run([
        'python', '-m', 'twine', 'upload',
        '--config-file', str(pypirc_path),
        'dist/*'
    ], check=True)
    print("✓ Uploaded to PyPI")

def main():
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        print("🔨 Building and uploading pytest-alerts")
        print("=====================================")
        
        # Clean previous builds
        clean_build_dirs()
        
        # Build the package
        build_package()
        
        # Upload to PyPI
        upload_to_pypi()
        
        print("\n✨ All done! Package has been built and uploaded successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Command failed with exit code {e.returncode}")
        print(f"Command: {' '.join(e.cmd)}")
        if e.output:
            print(f"Output: {e.output.decode()}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()
