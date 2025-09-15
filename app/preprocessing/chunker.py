# Chunk text into smaller chunks 
def chunk_by_chapter(text, delimiter="Chapter"):
    chapters = text.split(delimiter)
    chunks = []
    for chapter in chapters:
        if chapter.strip():
            chunks.append(delimiter + chapter.strip())  
    return chunks
