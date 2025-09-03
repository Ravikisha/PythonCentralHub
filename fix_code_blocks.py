import os
import re
import glob

def fix_code_blocks(file_path):
    print(f'Processing: {file_path}')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count existing python blocks without title
    python_blocks = re.findall(r'```python(?!\s+title=)', content)
    if not python_blocks:
        return False
    
    print(f'  Found {len(python_blocks)} python blocks without title')
    
    # Get the filename for the title
    filename = os.path.basename(file_path).replace('.mdx', '.py')
    
    # Replace python blocks without title
    # Pattern to match ```python without title= following it
    pattern = r'```python(?!\s+title=)'
    replacement = f'```python title="{filename}" showLineNumbers{{1}}'
    
    new_content = re.sub(pattern, replacement, content)
    
    # Check if any changes were made
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# Find all mdx files in projects folder
project_files = glob.glob('src/content/docs/projects/**/*.mdx', recursive=True)
print(f'Found {len(project_files)} MDX files')

updated_files = []
for file_path in project_files:
    if fix_code_blocks(file_path):
        updated_files.append(file_path)

print(f'\nUpdated {len(updated_files)} files:')
for file in updated_files:
    print(f'  ✓ {file}')
