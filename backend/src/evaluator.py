import string
from collections import Counter

#class for evaluating parser output
class Evaluator:

    def __init__(self, gs_txt: str, parsed_txt: str):
        self.gs_txt = gs_txt
        self.parsed_txt = parsed_txt

    #clean text
    def strip_txt(self, text: str): #make the two comparable (lower, strip markdown if necessary, links...)
        text = text.lower()
        #TO DO: add link stripper

        return text

    #this method returns a list of token (words)
    def tokenization(self, text: str):

        text = self.strip_txt(text)
        cleaning_rule = str.maketrans('', '', string.punctuation) #strips punctuation
        clean_txt = text.translate(cleaning_rule)
        clean_list = clean_txt.split() #creates list of word

        return clean_list
    
    #calculates the three core metrics: precision, recall, F1-Score
    def calculation(self, G: int, E: int, matches: int): 
        
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

        marks = self.calculation(sum(gs_set.values()), sum(ps_set.values), sum((gs_set & ps_set).values())) #matches = G intersection E
        if marks["F1"] < 0.6:
            grade = "Scarso"
        elif marks["F1"] > 0.8:
            grade = "Buono"
        else:
            grade = "Medio"

        return f"{grade}  ->  Precision = {marks["P"]}, Recall = {marks["R"]}, F1 = {marks["F1"]}\n"
    
     #time complexity = O(n*m), space complexity = O(m) (Traceback approach, there's no need to retrieve the actual common words)
    @staticmethod
    def lcs_length(A: list, B: list):

        m, n = len(A), len(B)
        prev = [0] * (n + 1)
        for i in range(1, m + 1):
            curr = [0] * (n + 1)
            for j in range(1, n + 1):
                if A[i - 1] == B[j - 1]:
                    curr[j] = prev[j - 1] + 1
                else:
                    curr[j] = max(prev[j], curr[j - 1])
            prev = curr
    
        return prev[n] #last element of last row contains lcs length


    def rouge_l_evaluation(self):
        
        gs_list = self.tokenization(self.gs_txt) #get a list of token
        ps_list = self.tokenization(self.parsed_txt)
        matches = self.lcs_length(gs_list, ps_list)
        marks = self.calculation(len(gs_list), len(ps_list), matches)

        if marks["F1"] < 0.6:
            grade = "Scarso"
        elif marks["F1"] > 0.8:
            grade = "Buono"
        else:
            grade = "Medio"

        return f"{grade}  ->  Precision = {marks["P"]}, Recall = {marks["R"]}, F1 = {marks["F1"]}\n"


