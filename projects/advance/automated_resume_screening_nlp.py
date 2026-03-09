"""
Automated Resume Screening using NLP

Features:
- Resume parsing
- Keyword extraction
- Scoring and ranking
- Modular design
- CLI interface
- Error handling
"""
import os
import sys
import re
import json
import glob
from collections import Counter
from typing import List, Dict

class ResumeParser:
    def __init__(self, keywords: List[str]):
        self.keywords = set(keywords)

    def parse(self, filepath: str) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        words = re.findall(r'\w+', text.lower())
        keyword_matches = [w for w in words if w in self.keywords]
        score = len(keyword_matches)
        return {
            'file': os.path.basename(filepath),
            'score': score,
            'keywords': Counter(keyword_matches)
        }

class ResumeScreening:
    def __init__(self, resume_dir: str, keywords: List[str]):
        self.resume_dir = resume_dir
        self.keywords = keywords
        self.parser = ResumeParser(keywords)
        self.results = []

    def screen(self):
        files = glob.glob(os.path.join(self.resume_dir, '*.txt'))
        for f in files:
            result = self.parser.parse(f)
            self.results.append(result)
        self.results.sort(key=lambda x: x['score'], reverse=True)

    def report(self):
        print("Screening Results:")
        for r in self.results:
            print(f"{r['file']}: Score={r['score']} Keywords={dict(r['keywords'])}")

    def save(self, outpath: str):
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 3:
            print("Usage: python automated_resume_screening_nlp.py <resume_dir> <keywords_file>")
            sys.exit(1)
        resume_dir = sys.argv[1]
        keywords_file = sys.argv[2]
        with open(keywords_file, 'r', encoding='utf-8') as f:
            keywords = [line.strip().lower() for line in f if line.strip()]
        screening = ResumeScreening(resume_dir, keywords)
        screening.screen()
        screening.report()
        screening.save('screening_results.json')
        print("Results saved to screening_results.json")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
