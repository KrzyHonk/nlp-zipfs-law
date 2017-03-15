from ebooklib import epub
import re
import html
import spacy

def example():
    book = epub.read_epub('hitchhiker.epub')
    for document in book.get_items_of_type(9):
        content = document.get_content().decode("utf-8")
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

        # Remove HTML tgs
        # Remove well-formed tags, fixing mistakes by legitimate users
        no_tags = tag_re.sub(' ', content)
        # Clean up anything else by escaping
        preprocessed_content = html.escape(no_tags).replace("\n"," ").strip()
        print(preprocessed_content)

        nlp = spacy.load('en')
        doc = nlp(preprocessed_content)
        for word in doc:
            print(word.text, word.pos_)
        reuters_words = [w.text.lower() for w in doc]
        words = set(reuters_words)
        counts = [(w, reuters_words.count(w)) for w in words]
        print(counts)
example()