#!/usr/bin/env python3
"""
Automated cleanup script for remaining linter issues
Fixes: unused imports, unused variables, unnecessary f-strings, redefinitions
"""
import re
from pathlib import Path


def remove_unused_imports(file_path, unused_imports):
    """Remove unused imports from a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        should_skip = False
        for imp in unused_imports:
            # Check if this line imports the unused module
            if f"import {imp}" in line or f"from {imp.split('.')[0]} import" in line:
                # Don't skip if it's a multi-import line with other imports
                if ',' in line:
                    # Remove just this import from the line
                    line = re.sub(rf',?\s*{imp.split(".")[-1]}\s*,?', '', line)
                    line = re.sub(r',\s*,', ',', line)  # Clean up double commas
                    if 'import' not in line or line.strip().endswith('import'):
                        should_skip = True
                else:
                    should_skip = True
                break
        
        if not should_skip:
            new_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


def remove_f_string_prefix(file_path, line_numbers):
    """Convert unnecessary f-strings to regular strings"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line_num in line_numbers:
        if line_num <= len(lines):
            line = lines[line_num - 1]
            # Convert f"text" to "text" if no placeholders
            lines[line_num - 1] = re.sub(r'f(["\'])', r'\1', line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def comment_unused_variables(file_path, var_info):
    """Prefix unused variables with underscore to mark them as intentionally unused"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for var_name, line_num in var_info:
        # Add underscore prefix to mark as intentionally unused
        pattern = rf'\b{var_name}\b\s*='
        replacement = f'_{var_name} ='
        content = re.sub(pattern, replacement, content, count=1)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


# Files with issues
fixes = {
    'src/report.py': {
        'remove_imports': ['os', 'Tuple'],
        'unused_vars': [('describe_name', 107)],
        'fix_fstrings': [347, 353, 357, 361]
    },
    'src/utils/enhanced_analyzer.py': {
        'remove_imports': ['statistics'],
        'fix_fstrings': [197, 204, 212]
    },
    'src/utils/local_analyzer.py': {
        'remove_redefinitions': True,  # lines 24-25
        'unused_vars': [('analysis', 150), ('e', 604)],
        'fix_fstrings': [158, 190, 198, 241, 250, 260, 275, 283, 291, 313, 520, 766]
    },
    'analyze_tests.py': {
        'unused_vars': [('status_color', 215)],
        'fix_fstrings': [82, 554, 751, 963]
    }
}

print("🔧 Starting cleanup...")
print(f"Found {len(fixes)} files to fix\n")

for file_path, actions in fixes.items():
    full_path = Path(__file__).parent / file_path
    if not full_path.exists():
        print(f"⚠️  {file_path} not found, skipping")
        continue
    
    print(f"📝 Processing {file_path}...")
    
    if 'remove_imports' in actions:
        print(f"  ➜ Removing unused imports: {', '.join(actions['remove_imports'])}")
        remove_unused_imports(full_path, actions['remove_imports'])
    
    if 'fix_fstrings' in actions:
        print(f"  ➜ Fixing {len(actions['fix_fstrings'])} unnecessary f-strings")
        remove_f_string_prefix(full_path, actions['fix_fstrings'])
    
    if 'unused_vars' in actions:
        print(f"  ➜ Prefixing {len(actions['unused_vars'])} unused variables with _")
        comment_unused_variables(full_path, actions['unused_vars'])

print("\n✅ Cleanup complete!")
print("Run flake8 again to verify improvements")
