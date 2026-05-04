# Minerva Parser Project

## Authors
| **Chiara De Benedictis** 
| **Alfredo De Meo**
| **Filippo Bassi** 

---
## Introduction
The **Minerva Parser** is a highly modular system engineered for the automated acquisition and analysis of documents from heterogeneous web sources.
The primary objective is to extract clean, relevant textual data in Markdown format, evaluate its extraction quality against a predefined gold standard (GS) and present the results on a simple webpage interface.
The system was developed serving as a foundational data pipeline component for the Italian national LLM, Minerva.
The project implements custom parsing strategies for the designated domains:`www.my-personaltrainer.it`, `it.wikipedia.org`, `www.premierleague.com`, `www.un.org`.

## 1. Methodology and Architecture
This section analyzes the general architecture of the project and the specific responsibilities of the individual modules.

### 1.1 Gold Standard (gs_data)
Gold standards were built for each domain: each contains a collection of 10 JSON objects holding the URLs considered representative of the entire domain (weight was given to structural and/or topic differences).

### 1.2 Backend

#### 1.2.1 Parsers
Parsing operations were developed using the open-source **Crawl4ai** library and customizing its configurations. The architectural choice involved creating a general superclass defining: default attributes, the abstract domain property, and a general parsing method. The subclasses, differentiated by domain, feature the following specifications:
* **Selectors to consider and/or ignore:** obtained through manual analysis of the source codes of the chosen URLs.
* **Delay time:** only where necessary, fundamental for parsing JavaScript paginations.
* **Magic Mode:** only in the presence of anti-bot systems, allowing them to be bypassed by simulating human navigation.
* **Text cleaning via regular expressions:** custom functions were used for each domain.

#### 1.2.2 Rest
The `server.py` module contains an API server that exposes the REST APIs for parsing, the gold standard, and evaluation on port `8003`. Output validations are performed via Pydantic. The `Zero_Initializer` function generates a dictionary mirroring a Pydantic model, acting as an accumulator for averages and a zero-fallback to prevent API crashes.

#### 1.2.3 Factory
The choice to implement a Factory design pattern stems from the need to associate individual domains with the correct subclass. The `create` method is called by the backend server and returns the correct Parser object.

#### 1.2.4 Evaluator
The `evaluator.py` module contains the Evaluator class, composed of various methods that evaluate the parsed text by comparing it with its gold standard.

### 1.3 Frontend
A graphical web interface is implemented (using Jinja2 for template rendering) along with a frontend server that handles user requests and coordinates calls to the backend. It returns: the raw HTML, the parsed text, and the gold standard if present.

### 1.4 Docker Compose
The project is containerized using Docker. Docker Compose manages and connects two containers: 
* **Backend:** exposes port `8003` and uses volumes to synchronize and save data on the physical computer.
* **Frontend:** exposes port `8004` and has a dependency that forces it to start only after the backend. 
The two containers communicate with each other in a private environment.

---

## 2. Optimizations
Below are some of the strategies devised to improve code efficiency.

### 2.1 Parser Optimizations
The implementation features a single general `parser_url(url: str)` function; this performs a single web request and returns the complete HTML, delegating all specific parsing operations to `parser_url2(url: str, html_text: str)`. This separation allows experimenting with different CSS selectors without having to repeat the web crawl more than once, and avoids repeated delays required for the complete loading of JavaScript pages.

### 2.2 Server Optimizations
The frontend uses the `asyncio.gather` function, which ensures that backend calls for all domains start concurrently rather than sequentially. In the backend, dictionaries were preferred for data structures requiring frequent lookups, achieving an **O(1)** complexity in the average case compared to **O(n)** for searches on lists.

---

## 3. Results/Evaluation
Four evaluation methods were implemented to assess the parsers:
* **Token-Level (TKE) and Rouge-2 (R-2):** reveal whether the parser loses content (low recall) or introduces noise (low precision). Rouge-2 adds sensitivity to text order by using consecutive word pairs instead of a single token.
* **TF-IDF Cosine Similarity (TF-IDF):** Represents texts as vectors where rare and distinctive words have a higher weight than common ones, measuring the angle between them. It captures the thematic and semantic similarity between the two texts.
* **Information Density Score (IDS):** calculates the proportion of meaningful words against the total after removing specific stopwords based on the language. It does not necessarily require comparison with the gold standard. It signals the presence of noise, which would degrade the performance of a downstream LLM.

| Domain | TKE (F1) | R-2 (F1) | IDS | TF-IDF |
| :--- | :--- | :--- | :--- | :--- |
| **my-personaltrainer.it** | 0.979 | 0.976 | 0.633 | 0.992 |
| **it.wikipedia.org** | 0.977 | 0.968 | 0.660 | 0.919 |
| **premierleague.com** | 0.899 | 0.888 | 0.752 | 0.980 |
| **un.org** | 0.937 | 0.934 | 0.615 | 0.968 |

The scores demonstrate that the parsed text is suitable for use by an LLM, with high content preservation (recall > 0.93)[^2] and sufficient information density (IDS > 0.61).

---

## 4. Conclusion

### 4.1 Limits
Domains with dynamic JavaScript and anti-bot systems require delay and magic mode, slowing down parsing despite the optimization of the single web crawl. Furthermore, sites with heterogeneous architecture (`un.org`) show reduced precision due to the difficulty in isolating relevant content.

### 4.2 Strengths
The system supports multilingual evaluation (FR, EN, IT, ES) and handles large texts quickly thanks to the implemented optimizations.

### 4.3 Future Developments
The evaluation method could be adapted to ensure greater reliability even in the presence of short texts.

---
**Methodological Notes**
[^1]: LaTeX: Kept in gold texts because it is relevant for processing via LLM. The parsed text contains irrelevant content excluded from the gold standards (which cannot be filtered via code); its presence sometimes reduced the parser's precision.
[^2]: See the `full_gs_eval` results.
