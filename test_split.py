import re
import sys

def test_split(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
        
    print(f"Original file length: {len(content)} characters\n")
    
    # Split using the exact same regex as send_today.py
    parts = re.split(r'#{2,}', content)
    
    print(f"Found {len(parts)} segments after splitting:\n")
    
    for i, part in enumerate(parts):
        cleaned_part = part.strip()
        preview = cleaned_part[:100].replace('\n', ' ') + ('...' if len(cleaned_part) > 100 else '')
        
        print(f"--- Segment {i} (Length: {len(cleaned_part)} characters) ---")
        if cleaned_part:
            print(preview)
        else:
            print("[Empty Segment]")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_split.py <path_to_your_text_file.txt>")
    else:
        test_split(sys.argv[1])
