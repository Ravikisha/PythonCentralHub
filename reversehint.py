import os
import re

def revert_mdx_files(directory="."):
    # Match the hint block just like the previous script
    hint_pattern = re.compile(r'hint=\{\`(.*?)\`\}', re.DOTALL)

    def revert_inner_backticks(match):
        inner_content = match.group(1)
        # Find escaped backticks (\`) and replace them with standard backticks (`)
        reverted_content = inner_content.replace(r'\`', '`')
        # Reconstruct the outer boundary
        return f'hint={{`{reverted_content}`}}'

    files_modified = 0

    # Walk recursively through all folders
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mdx"):
                filepath = os.path.join(root, file)
                
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Apply the revert replacement
                new_content = hint_pattern.sub(revert_inner_backticks, content)
                
                # Only write back if changes were actually made
                if new_content != content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Reverted: {filepath}")
                    files_modified += 1
                    
    print(f"\nDone! Reverted changes in {files_modified} files.")

if __name__ == "__main__":
    revert_mdx_files("src/content/docs")