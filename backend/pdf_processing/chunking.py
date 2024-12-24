
def chunk_text(text, chunk_size=500):
    """
    Splits the input text into chunks of a given size.

    Parameters:
    - text (str): Text to be chunked.
    - chunk_size (int): Maximum number of characters per chunk.

    Returns:
    - list: List of text chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if sum(len(w) for w in current_chunk) + len(word) + len(current_chunk) <= chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks
