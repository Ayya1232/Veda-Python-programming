"""
Read and Process a Text File
-----------------------------
Reads a text file and generates statistics:
- Line count
- Word count
- Character count

Handles missing files gracefully and avoids loading very large
files into memory all at once (reads line-by-line instead).
"""

import os


def get_file_stats(file_path):
    """
    Read a text file and compute line, word, and character counts.

    Uses 'with open()' so the file is automatically closed even if
    an error occurs. Reads the file line-by-line (streaming) rather
    than loading the whole file into memory at once, which matters
    for very large files.

    Returns a dict with the stats, or None if the file could not
    be read.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return None

    line_count = 0
    word_count = 0
    char_count = 0

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:                 # streams the file, one line at a time
                line_count += 1
                word_count += len(line.split())
                char_count += len(line)
    except PermissionError:
        print(f"Error: Permission denied when trying to read '{file_path}'.")
        return None
    except UnicodeDecodeError:
        print(f"Error: '{file_path}' isn't a readable text file (bad encoding).")
        return None
    except OSError as e:
        print(f"Error: Could not read '{file_path}' ({e}).")
        return None

    return {
        "lines": line_count,
        "words": word_count,
        "characters": char_count,
    }


def print_stats(file_path, stats):
    print(f"\nStatistics for: {file_path}")
    print("-" * 40)
    print(f"Lines      : {stats['lines']}")
    print(f"Words      : {stats['words']}")
    print(f"Characters : {stats['characters']}")


def main():
    file_path = input("Enter the path to a text file: ").strip()
    stats = get_file_stats(file_path)
    if stats:
        print_stats(file_path, stats)


if __name__ == "__main__":
    main()