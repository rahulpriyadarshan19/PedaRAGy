# Chunk text into smaller chunks 
# Chunk by chapter, section, paragraph, sentence, and word
class Chunker:
    def chunk_by_chapter(self, text, delimiter="Chapter"):
        chapters = text.split(delimiter)
        chunks = []
        for chapter in chapters:
            if chapter.strip():
                chunks.append(delimiter + chapter.strip())  
        return chunks
    
    def chunk_by_section(self, text, delimiter="Section"):
        sections = text.split(delimiter)
        chunks = []
        for section in sections:
            if section.strip():
                chunks.append(delimiter + section.strip())
        return chunks
    
    def chunk_by_paragraph(self, text, delimiter="Paragraph"):
        paragraphs = text.split(delimiter)
        chunks = []
        for paragraph in paragraphs:
            if paragraph.strip():
                chunks.append(delimiter + paragraph.strip())
        return chunks
    
    def chunk_by_sentence(self, text, delimiter="Sentence"):
        sentences = text.split(delimiter)
        chunks = []
        for sentence in sentences:
            if sentence.strip():
                chunks.append(delimiter + sentence.strip())
        return chunks
    
    def chunk_by_word(self, text, delimiter="Word"):
        words = text.split(delimiter)
        chunks = []
        for word in words:
            if word.strip():
                chunks.append(delimiter + word.strip())
        return chunks
    
if __name__ == "__main__":
    chunker = Chunker()
    text = "This is a test sentence. This is another test sentence. This is a third test sentence."
    print(chunker.chunk_by_chapter(text))
    print(chunker.chunk_by_section(text))
    print(chunker.chunk_by_paragraph(text))
    print(chunker.chunk_by_sentence(text))
    print(chunker.chunk_by_word(text))
