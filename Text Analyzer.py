"""
Word and Character Counter
---------------------------
Accepts a paragraph of text and calculates:
- Number of characters (with and without spaces)
- Number of words
- Number of sentences
- Number of spaces

Task 11 - Python Programming Track
"""

import string


def count_characters(text, include_spaces=True):
    """Count characters in the text. Optionally exclude spaces."""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", ""))


def count_words(text):
    """Count words using split(), which handles multiple/irregular whitespace."""
    words = text.split()
    return len(words)


def count_sentences(text):
    """
    Count sentences by counting sentence-ending punctuation (. ! ?).
    Consecutive punctuation (e.g. "...", "?!") counts as a single sentence end.
    """
    sentence_enders = ".!?"
    count = 0
    prev_char_was_ender = False

    for char in text:
        if char in sentence_enders:
            if not prev_char_was_ender:
                count += 1
            prev_char_was_ender = True
        else:
            prev_char_was_ender = False

    # Fallback: if no punctuation was found but there is text,
    # treat the whole non-empty text as one sentence.
    if count == 0 and text.strip():
        count = 1

    return count


def count_spaces(text):
    """Count all whitespace characters that are literal spaces."""
    return text.count(" ")


def count_punctuation(text):
    """Bonus stat: count punctuation characters."""
    return sum(1 for char in text if char in string.punctuation)


def analyze_text(text):
    """Run the full analysis and return a dictionary of statistics."""
    return {
        "characters_with_spaces": count_characters(text, include_spaces=True),
        "characters_without_spaces": count_characters(text, include_spaces=False),
        "words": count_words(text),
        "sentences": count_sentences(text),
        "spaces": count_spaces(text),
        "punctuation_marks": count_punctuation(text),
    }


def print_report(text, stats):
    """Nicely print the analysis results."""
    print("\n" + "=" * 50)
    print("TEXT ANALYSIS REPORT")
    print("=" * 50)
    preview = text if len(text) <= 80 else text[:77] + "..."
    print(f"Input preview: {preview!r}")
    print("-" * 50)
    print(f"Characters (with spaces):    {stats['characters_with_spaces']}")
    print(f"Characters (without spaces): {stats['characters_without_spaces']}")
    print(f"Words:                       {stats['words']}")
    print(f"Sentences:                   {stats['sentences']}")
    print(f"Spaces:                      {stats['spaces']}")
    print(f"Punctuation marks:           {stats['punctuation_marks']}")
    print("=" * 50 + "\n")


def get_paragraph_input():
    """Prompt the user for a paragraph, handling empty input gracefully."""
    text = input("Enter a paragraph of text to analyze:\n> ")
    return text


def main():
    sample_paragraph = (
        "Python is a powerful programming language. It is widely used for "
        "web development, data science, and automation! Have you tried it yet? "
        "Many beginners find it easy to learn, and many experts rely on it daily."
    )

    print("Word and Character Counter")
    print("Press Enter without typing anything to use a sample paragraph instead.\n")

    text = get_paragraph_input()

    if not text.strip():
        print("\nNo input detected. Handling empty input gracefully...")
        print("Using a sample paragraph for demonstration purposes.")
        text = sample_paragraph

    stats = analyze_text(text)
    print_report(text, stats)


if __name__ == "__main__":
    main()