import os
import re

def fix_mdx_files(directory="."):
    # Pattern to match: hint={` followed by anything up to the closing `}
    # re.DOTALL ensures it works even if your hint spans multiple lines
    hint_pattern = re.compile(r'hint=\{\`(.*?)\`\}', re.DOTALL)

    def replace_inner_backticks(match):
        inner_content = match.group(1)
        # Escape any backtick that doesn't already have a backslash
        fixed_content = re.sub(r'(?<!\\)`', r'\\`', inner_content)
        # Reconstruct the outer boundary safely
        return f'code={{`{fixed_content}`}}'

    files_modified = 0

    # Walk recursively through all folders
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mdx"):
                filepath = os.path.join(root, file)
                
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Apply the regex replacement
                new_content = hint_pattern.sub(replace_inner_backticks, content)
                
                # Only write back if changes were actually made
                if new_content != content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Fixed: {filepath}")
                    files_modified += 1
                    
    print(f"\nDone! Fixed hints in {files_modified} files.")

if __name__ == "__main__":
    fix_mdx_files("./src/content/docs")