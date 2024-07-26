from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from config import Config

# init model to extract entity
tokenizer = AutoTokenizer.from_pretrained(Config.tokenizer_ner_model)
model = AutoModelForTokenClassification.from_pretrained(Config.model_ner)


def extract_main_entity(text):
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, grouped_entities=True)
    ner_results = nlp(text)

    result = []
    for entity in ner_results:
        result.append(entity['word'])

    return ', '.join(result)


print(extract_main_entity("my name is Oleksii"))