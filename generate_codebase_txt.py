#!/usr/bin/env python3
import os
import fnmatch
from datetime import datetime

def should_ignore(path, ignore_patterns):
    """Check if a path should be ignored based on common ignore patterns."""
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in path.split(os.sep)):
            return True
    return False

def export_codebase_to_text(source_dir='.', output_file=None):
    """
    Export all code files from the codebase to a single text file.
    
    Args:
        source_dir: Source directory (default: current directory)
        output_file: Output text file (default: 'codebase_export_YYYY-MM-DD.txt')
    """
    # Common ignore patterns (similar to .gitignore defaults)
    common_ignore_patterns = [
        '*.pyc', '__pycache__', '__pycache__/*',
        '.git', '.git/*', '.gitignore', '.github/*',
        '.idea/*', '.vscode/*', '*.swp', '*.swo',
        'node_modules', 'node_modules/*',
        'venv', 'venv/*', 'env', 'env/*',
        'build', 'build/*', 'dist', 'dist/*',
        '*.log', 'logs/*', '*.tmp',
        '*.zip', '*.tar.gz', '*.tgz',
        '*.exe', '*.dll', '*.so', '*.dylib',
        '*.class', '*.jar',
        '.DS_Store', 'Thumbs.db',
        # Ignore binary/media files
        '*.jpg', '*.jpeg', '*.png', '*.gif', '*.ico', '*.svg',
        '*.mp3', '*.mp4', '*.avi', '*.mov',
        '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
        '*.ttf', '*.otf', '*.woff', '*.woff2',
        # Ignore the script itself and its output
        'generate_codebase_txt.py', 'codebase_export_*.txt'
    ]
    
    # Set default output file with timestamp
    if output_file is None:
        timestamp = datetime.now().strftime('%Y-%m-%d')
        output_file = f'codebase_export_{timestamp}.txt'
    
    # Count processed files
    processed_files = 0
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        # Walk through the source directory
        for root, dirs, files in os.walk(source_dir):
            # Process each file
            for file in files:
                source_path = os.path.join(root, file)
                # Get relative path
                rel_path = os.path.relpath(source_path, source_dir)
                
                # Skip if file should be ignored
                if should_ignore(rel_path, common_ignore_patterns):
                    continue
                
                # Skip files that are likely binary
                if os.path.getsize(source_path) > 10 * 1024 * 1024:  # Skip files > 10MB
                    print(f"Skipping large file: {rel_path}")
                    continue
                
                # Try to read the file
                try:
                    with open(source_path, 'r', encoding='utf-8') as in_file:
                        content = in_file.read()
                        
                    # Write file header
                    out_file.write(f"\n\n{'=' * 80}\n")
                    out_file.write(f"FILE: {rel_path}\n")
                    out_file.write(f"{'=' * 80}\n\n")
                    
                    # Write file content
                    out_file.write(content)
                    processed_files += 1
                    print(f"Added: {rel_path}")
                except UnicodeDecodeError:
                    print(f"Skipping binary file: {rel_path}")
                except Exception as e:
                    print(f"Error processing {rel_path}: {e}")
    
    print(f"\nExported {processed_files} files to {output_file}")
    
    # Print file size
    file_size = os.path.getsize(output_file)
    print(f"File size: {file_size / 1024:.2f} KB")
    
    return output_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Export codebase to a single text file')
    parser.add_argument('--source', default='.', help='Source directory (default: current directory)')
    parser.add_argument('--output', default=None, help='Output text file')
    
    args = parser.parse_args()
    export_codebase_to_text(args.source, args.output) 