import string
from collections import Counter
import re 

#class for evaluating parser output
class Evaluator:

    def __init__(self, gs_txt: str, parsed_txt: str):
        self.gs_txt = gs_txt
        self.parsed_txt = parsed_txt
        self.chunk_size = 500

    #clean text
    def strip_txt(self, text: str): #make the two comparable (lower, strip markdown if necessary, links...)
        text = text.lower()
        #TO DO: add link stripper

        return text

    #this method returns a list of token (words)
    @staticmethod
    def tokenization(text: str):

        #clean text
        def strip_txt(text: str): #make the two comparable (lower, strip markdown if necessary, links...)
            text = text.lower()

            text = re.sub(r'\*+([^*]+)\*+', r'\1', text) #grassettp
            text = re.sub(r'\_+([^_]+)\_+', r'\1', text) #corsivo
            text = re.sub(r'\#+\s?([^#]+)', r'\1', text) #titoli
            text = re.sub(r'\[([^\]]+)\]\((?:[^)\\]|\\.)*\)', r'\1', text) #link(??)

            return text

        text = strip_txt(text)
        cleaning_rule = str.maketrans('', '', string.punctuation) #strips punctuation
        clean_txt = text.translate(cleaning_rule)
        clean_list = clean_txt.split() #creates list of word

        return clean_list
    
    #calculates the three core metrics: precision, recall, F1-Score
    @staticmethod
    def calculation(G: int, E: int, matches: int): 
        
        if not E:
            precision = 0
        else:
            precision = matches / E
        recall = matches / G #this will never be 0

        if not precision + recall:
            F1 = 0
        else:
            F1 = 2*(precision*recall / (precision+recall))

        return {"P" : precision, "R" : recall, "F1" : F1}

    def token_level_eval(self): 

        gs_set = Counter(self.tokenization(self.gs_txt)) #get a Counter of token, goal: be more accurate with token evaluation
        ps_set = Counter(self.tokenization(self.parsed_txt))

        marks = self.calculation(sum(gs_set.values()), sum(ps_set.values()), sum((gs_set & ps_set).values())) #matches = G intersection E
        if marks["F1"] < 0.6:
            grade = "Scarso"
        elif marks["F1"] > 0.8:
            grade = "Buono"
        else:
            grade = "Medio"

        return f"{grade}  ->  Precision = {marks['P']}, Recall = {marks['R']}, F1 = {marks['F1']}\n"
    
    @staticmethod
    def extract_ngrams(tokens, n):
        return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]

    #takes a bigram (two consecutive tokens) instead of a single one, then the calculation method is the same as token - level
    def rouge_2_eval(self): #very short texts are penalized as a text of length n produces n-1 bigrams.

        gs_bigram_set = Counter(self.extract_ngrams(self.tokenization(self.gs_txt), 2)) #get a Counter of token, goal: be more accurate with token evaluation
        ps_bigram_set = Counter(self.extract_ngrams(self.tokenization(self.parsed_txt), 2))

        marks = self.calculation(sum(gs_bigram_set.values()), sum(ps_bigram_set.values()), sum((gs_bigram_set & ps_bigram_set).values())) #matches = G intersection E
        if marks["F1"] < 0.6:
            grade = "Scarso"
        elif marks["F1"] > 0.8:
            grade = "Buono"
        else:
            grade = "Medio"

        return f"{grade}  ->  Precision = {marks['P']}, Recall = {marks['R']}, F1 = {marks['F1']}\n"
    
    
