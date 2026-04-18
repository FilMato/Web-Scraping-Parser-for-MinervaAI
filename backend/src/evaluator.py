import string
from collections import Counter
from nltk.corpus import stopwords
from math import log, sqrt
import re 

#class for evaluating parser output
class Evaluator:

    def __init__(self):
        self._languages_stopwords = {
            'english' : set(stopwords.words('english')), 
            'italian' : set(stopwords.words('italian')), 
            'spanish' : set(stopwords.words('spanish')), 
            'french' : set(stopwords.words('french'))
            }

    #this method returns a list of token (words)
    @staticmethod
    def _tokenization(text: str) -> list:

        #clean text
        def strip_txt(text: str) -> str: #make the two comparable (lower, strip markdown if necessary, links...)
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
    def _calculation(G: int, E: int, matches: int) -> dict: 
        
        if not E:
            precision = 0
        else:
            precision = matches / E
        
        if not G:
            recall = 0
        else:
            recall = matches / G 

        if not precision + recall:
            F1 = 0
        else:
            F1 = 2*(precision*recall / (precision+recall))

        return {"precision": precision, 
                "recall": recall,
                "f1": F1}
    
    @staticmethod
    def _extract_ngrams(tokens, n) -> list:
        return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
    
    def _detect_language(self, tokenized_txt: list) -> str:
            
            input_txt = Counter(tokenized_txt)
            max_cnt = 0
            detected_language = ''
            for language in self._languages_stopwords:
                curr_set = self._languages_stopwords[language]
                curr_intersection = sum((input_txt & Counter(curr_set)).values())
                if curr_intersection > max_cnt:
                    max_cnt = curr_intersection
                    detected_language = language

            return detected_language
    
    def _filter_stopwords(self, tokenized_txt: list, language: str) -> list:
        return [word for word in tokenized_txt if word not in self._languages_stopwords[language]]
    
    @staticmethod
    def _tf(tokens: list) -> dict:

        cnt = Counter(tokens)
        token_count = len(tokens)
        tf = {}
        for word in cnt:
            tf[word] = cnt[word] / token_count

        return tf
    
    @staticmethod
    def _idf(gs_tokens: list, ps_tokens: list) -> dict:

        gs_tokens_set = set(gs_tokens)
        ps_tokens_set = set(ps_tokens)
        combined_vocabulary = gs_tokens_set.union(ps_tokens_set)
        idf = {}
        for word in combined_vocabulary:
            docs_containing_word = 0
            if word in gs_tokens_set:
                docs_containing_word += 1
            if word in ps_tokens_set:
                docs_containing_word += 1
            idf[word] = 1 + log(2 + 1 / docs_containing_word + 1)
            #spiegazione della formula : 2 = documenti totali, i +1 nel logaritmo servono a proteggere
            #dall'errore di divisione per 0 (come se ci fosse un documento in più che contiene tutte le parole)
            #il +1 al di fuori dal logaritmo serve a dar peso alle parole contenute in entrambi i documenti, che altrimenti
            #peserebbero 0 (log(2/2) = log(1) = 0)

        return idf

    def _build_tf_idf(self, filtered_tokens_gs: list, filtered_tokens_ps: list) -> tuple[dict]:
        tf_gs_dict = self._tf(filtered_tokens_gs)
        tf_ps_dict = self._tf(filtered_tokens_ps)
        idf_dict = self._idf(filtered_tokens_gs, filtered_tokens_ps)

        tfidf_gs =  {}
        tfidf_ps = {}

        for word in idf_dict:
            tfidf_gs[word] = tf_gs_dict.get(word, 0) * idf_dict[word] #il vocabolario combinato contiene parole da entrambi i testi, .get(word, 0) fa in modo che se la parola non esiste il risultato sia 0 invece di avere un KeyError
            tfidf_ps[word] = tf_ps_dict.get(word, 0) * idf_dict[word]
        
        return tfidf_gs, tfidf_ps
    
    def _tfidf_cosine_similarity(self, ps_txt: str, gs_txt: str) -> float:
        
        tokens_gs = self._tokenization(gs_txt)
        filtered_gs = self._filter_stopwords(tokens_gs, self._detect_language(tokens_gs))
        tokens_ps = self._tokenization(ps_txt)
        filtered_ps = self._filter_stopwords(tokens_ps, self._detect_language(tokens_ps))
        
        tfidf_gs, tfidf_ps = self._build_tf_idf(filtered_gs, filtered_ps)
        dot_product = 0

        for word in tfidf_gs:
            dot_product += tfidf_gs[word] * tfidf_ps.get(word, 0)
        
        magnitude_gs = 0
        magnitude_ps = 0
        for word in tfidf_gs:
            magnitude_gs += pow(tfidf_gs[word], 2)
        for word in tfidf_ps:
            magnitude_ps += pow(tfidf_ps[word], 2)
        magnitude_gs = sqrt(magnitude_gs)
        magnitude_ps = sqrt(magnitude_ps)
        
        try:
            return dot_product / (magnitude_gs * magnitude_ps) 
        except ZeroDivisionError: #con un testo reale questa cosa non dovrebbe succedere ma il controllo va messo per sicurezza
            return 0


    def _information_density_score(self, ps_txt: str, gs_txt: str) -> dict:

        tokens_gs = self._tokenization(gs_txt)
        filtered_gs = self._filter_stopwords(tokens_gs, self._detect_language(tokens_gs))
        tokens_ps = self._tokenization(ps_txt)
        filtered_ps = self._filter_stopwords(tokens_ps, self._detect_language(tokens_ps))
        score_gs = len(filtered_gs) / len(tokens_gs)
        score_ps = len(filtered_ps) / len(tokens_ps)
        
        return {
            'Score gold standard' : score_gs,
            'Score parsed text' : score_ps,
            'Difference' : abs(score_gs - score_ps)
            }
    
    def _token_level_eval(self, parsed_txt:str, gs_txt:str) -> dict: 

        gs_set = Counter(self._tokenization(gs_txt)) #get a Counter of token, goal: be more accurate with token evaluation
        ps_set = Counter(self._tokenization(parsed_txt))
        marks = self._calculation(sum(gs_set.values()), sum(ps_set.values()), sum((gs_set & ps_set).values())) #matches = G intersection E
        
        return marks

    #takes a bigram (two consecutive tokens) instead of a single one, then the calculation method is the same as token - level
    def _rouge_2_eval(self, parsed_txt:str, gs_txt:str) -> dict: #very short texts are penalized as a text of length n produces n-1 bigrams.

        gs_bigram_set = Counter(self._extract_ngrams(self._tokenization(gs_txt), 2)) #get a Counter of token, goal: be more accurate with token evaluation
        ps_bigram_set = Counter(self._extract_ngrams(self._tokenization(parsed_txt), 2))
        marks = self._calculation(sum(gs_bigram_set.values()), sum(ps_bigram_set.values()), sum((gs_bigram_set & ps_bigram_set).values())) #matches = G intersection E
        
        return marks
    
    #funzione da usare nel server per POST/evaluate
    def eval_server(self, parsed_txt: str, gs_txt:str) -> dict: 

        return {
            "token_level_eval": self._token_level_eval(parsed_txt, gs_txt),
            "rouge_2_eval": self._rouge_2_eval(parsed_txt, gs_txt),
            "information_density_evaluation" : self._information_density_score(parsed_txt, gs_txt),
            "TF-IDF_cosine_similarity" : self._tfidf_cosine_similarity(parsed_txt, gs_txt)
        }
    
    
