import os
import re

# Set the path to your MDX files root directory
directory = './src/content/docs'

def fix_description_colons_recursive(root_dir):
    # os.walk yields a 3-tuple: (current_path, directories, files)
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith(".mdx") or filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                print(f"Processing: {os.path.relpath(filepath, root_dir)}")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                new_lines = []
                changed = False

                for line in lines:
                    # Only target the YAML frontmatter title
                    if line.startswith('title:'):
                        colons = [m.start() for m in re.finditer(':', line)]
                        
                        if len(colons) >= 2:
                            second_colon_index = colons[1]
                            # Replace second colon with a hyphen
                            line = line[:second_colon_index] + ' -' + line[second_colon_index+1:]
                            changed = True
                    
                    new_lines.append(line)

                if changed:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    # Printing the relative path so you can see where the change happened
                    print(f"Fixed: {os.path.relpath(filepath, root_dir)}")

fix_description_colons_recursive(directory)
import yaml

def find_broken_frontmatter(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith((".mdx", ".md")):
                filepath = os.path.join(root, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file has frontmatter (starts and ends with ---)
                if content.startswith('---'):
                    try:
                        # Extract the frontmatter block
                        parts = content.split('---')
                        if len(parts) >= 3:
                            frontmatter = parts[1]
                            # Try to load it as YAML
                            yaml.safe_load(frontmatter)
                    except yaml.YAMLError as exc:
                        print(f"\n❌ FOUND BROKEN FILE: {filepath}")
                        print(f"Error details: {exc}")
                        print("-" * 30)

find_broken_frontmatter(directory)