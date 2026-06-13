import spacy.cli
import nltk

def setup_resources():
    # Скачиваем модель языка
    spacy.cli.download("en_core_web_sm")
    # Скачиваем список стоп-слов
    nltk.download('stopwords')

if __name__ == "__main__":
    setup_resources()