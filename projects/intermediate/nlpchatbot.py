#!/usr/bin/env python3
"""
Advanced Chatbot with Natural Language Processing
A sophisticated chatbot using NLTK and spaCy for natural language understanding.

Features:
- Intent recognition and entity extraction
- Context-aware conversations
- Sentiment analysis
- Learning from conversations
- Multiple response generation strategies
- Conversation history and analytics

Requirements:
- nltk
- spacy
- scikit-learn
- textblob
- transformers (optional for advanced features)

Author: Python Central Hub
Date: 2025-09-05
"""

import nltk
import spacy
import re
import json
import random
import pickle
from datetime import datetime
from collections import defaultdict, deque
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np


class NLPChatbot:
    """Advanced chatbot with natural language processing capabilities."""
    
    def __init__(self):
        self.setup_nltk()
        self.setup_spacy()
        self.conversation_history = deque(maxlen=10)
        self.user_context = {}
        self.intent_classifier = None
        self.response_generator = ResponseGenerator()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_extractor = EntityExtractor()
        self.knowledge_base = self.load_knowledge_base()
        self.train_intent_classifier()
        
    def setup_nltk(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('taggers/averaged_perceptron_tagger')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("📦 Downloading NLTK data...")
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('wordnet')
            nltk.download('vader_lexicon')
    
    def setup_spacy(self):
        """Setup spaCy NLP pipeline."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️  spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def load_knowledge_base(self):
        """Load chatbot knowledge base and training data."""
        return {
            'intents': {
                'greeting': {
                    'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
                    'responses': [
                        "Hello! How can I help you today?",
                        "Hi there! What can I do for you?",
                        "Hey! Great to see you. How are you doing?",
                        "Hello! I'm here to assist you. What's on your mind?"
                    ]
                },
                'goodbye': {
                    'patterns': ['bye', 'goodbye', 'see you', 'farewell', 'take care'],
                    'responses': [
                        "Goodbye! Have a great day!",
                        "See you later! Take care!",
                        "Farewell! It was nice talking to you.",
                        "Bye! Feel free to come back anytime."
                    ]
                },
                'question': {
                    'patterns': ['what', 'how', 'why', 'when', 'where', 'who', '?'],
                    'responses': [
                        "That's an interesting question! Let me think about it.",
                        "I'd be happy to help you with that.",
                        "Good question! Here's what I know about that topic.",
                        "Let me provide you with some information on that."
                    ]
                },
                'help': {
                    'patterns': ['help', 'assist', 'support', 'can you help'],
                    'responses': [
                        "I'm here to help! What do you need assistance with?",
                        "Of course! I'd be glad to assist you.",
                        "I'm ready to help. What can I do for you?",
                        "Let me know what you need help with!"
                    ]
                },
                'programming': {
                    'patterns': ['python', 'code', 'programming', 'algorithm', 'function', 'variable'],
                    'responses': [
                        "Programming is fascinating! What specific aspect interests you?",
                        "I love talking about code! What programming topic can I help you with?",
                        "Great! Programming questions are my specialty. Fire away!",
                        "Coding is awesome! What would you like to learn about?"
                    ]
                },
                'compliment': {
                    'patterns': ['good', 'great', 'awesome', 'amazing', 'perfect', 'excellent'],
                    'responses': [
                        "Thank you! That's very kind of you to say.",
                        "I appreciate the compliment! Is there anything else I can help with?",
                        "That means a lot! I'm glad I could be helpful.",
                        "Thank you! I try my best to be useful."
                    ]
                },
                'name': {
                    'patterns': ['what is your name', 'who are you', 'your name'],
                    'responses': [
                        "I'm an AI chatbot created with Python and NLP technologies!",
                        "You can call me ChatBot! I'm here to help and have conversations.",
                        "I'm an AI assistant powered by natural language processing.",
                        "I'm ChatBot, your friendly AI conversation partner!"
                    ]
                },
                'feelings': {
                    'patterns': ['how are you', 'how do you feel', 'are you okay'],
                    'responses': [
                        "I'm doing great! Thanks for asking. How are you?",
                        "I'm functioning perfectly! How about you?",
                        "I'm excellent, thank you! What brings you here today?",
                        "I'm doing wonderful! How can I brighten your day?"
                    ]
                }
            },
            'facts': {
                'python': "Python is a high-level programming language known for its simplicity and readability.",
                'ai': "Artificial Intelligence is the simulation of human intelligence in machines.",
                'nlp': "Natural Language Processing helps computers understand and generate human language.",
                'machine learning': "Machine Learning enables computers to learn and improve from experience.",
            }
        }
    
    def train_intent_classifier(self):
        """Train a machine learning model for intent classification."""
        training_data = []
        training_labels = []
        
        for intent, data in self.knowledge_base['intents'].items():
            for pattern in data['patterns']:
                training_data.append(pattern.lower())
                training_labels.append(intent)
        
        # Create and train the classifier
        self.intent_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english')),
            ('clf', MultinomialNB())
        ])
        
        self.intent_classifier.fit(training_data, training_labels)
    
    def predict_intent(self, text):
        """Predict the intent of user input."""
        if not self.intent_classifier:
            return 'unknown'
        
        try:
            intent = self.intent_classifier.predict([text.lower()])[0]
            confidence = max(self.intent_classifier.predict_proba([text.lower()])[0])
            
            # Return intent only if confidence is above threshold
            return intent if confidence > 0.3 else 'unknown'
        except:
            return 'unknown'
    
    def process_message(self, user_input):
        """Process user message and generate appropriate response."""
        # Store conversation history
        self.conversation_history.append({
            'user': user_input,
            'timestamp': datetime.now(),
            'sentiment': self.sentiment_analyzer.analyze(user_input)
        })
        
        # Clean and preprocess input
        cleaned_input = self.preprocess_text(user_input)
        
        # Extract entities
        entities = self.entity_extractor.extract(user_input)
        
        # Predict intent
        intent = self.predict_intent(cleaned_input)
        
        # Generate response based on intent and context
        response = self.generate_response(intent, cleaned_input, entities)
        
        # Store bot response
        self.conversation_history.append({
            'bot': response,
            'timestamp': datetime.now(),
            'intent': intent
        })
        
        return response, intent
    
    def preprocess_text(self, text):
        """Clean and preprocess text input."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and question marks
        text = re.sub(r'[^\w\s\?]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def generate_response(self, intent, text, entities):
        """Generate appropriate response based on intent and context."""
        # Check for specific keywords first
        for fact_key, fact_value in self.knowledge_base['facts'].items():
            if fact_key in text:
                return f"Here's what I know about {fact_key}: {fact_value}"
        
        # Generate response based on intent
        if intent in self.knowledge_base['intents']:
            responses = self.knowledge_base['intents'][intent]['responses']
            base_response = random.choice(responses)
            
            # Personalize response if entities are found
            if entities:
                base_response += f"\n\nI noticed you mentioned: {', '.join(entities)}"
            
            return base_response
        
        # Fallback responses for unknown intents
        return self.response_generator.generate_fallback_response(text)
    
    def get_conversation_summary(self):
        """Get summary of current conversation."""
        if not self.conversation_history:
            return "No conversation history yet."
        
        user_messages = [msg for msg in self.conversation_history if 'user' in msg]
        bot_messages = [msg for msg in self.conversation_history if 'bot' in msg]
        
        summary = {
            'total_exchanges': len(user_messages),
            'avg_sentiment': np.mean([msg.get('sentiment', 0) for msg in user_messages]),
            'topics_discussed': self.extract_topics(),
            'conversation_length': len(self.conversation_history)
        }
        
        return summary
    
    def extract_topics(self):
        """Extract main topics from conversation history."""
        topics = set()
        for msg in self.conversation_history:
            if 'user' in msg:
                text = msg['user'].lower()
                # Simple keyword extraction
                for intent in self.knowledge_base['intents']:
                    for pattern in self.knowledge_base['intents'][intent]['patterns']:
                        if pattern in text:
                            topics.add(intent)
        return list(topics)


class SentimentAnalyzer:
    """Analyze sentiment of user messages."""
    
    def analyze(self, text):
        """Analyze sentiment using TextBlob."""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0
    
    def get_sentiment_label(self, polarity):
        """Convert polarity score to sentiment label."""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'


class EntityExtractor:
    """Extract named entities from text."""
    
    def __init__(self):
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except:
            pass
    
    def extract(self, text):
        """Extract entities using spaCy if available."""
        entities = []
        
        if self.nlp:
            doc = self.nlp(text)
            entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT']]
        
        # Fallback: simple pattern matching
        if not entities:
            entities = self.extract_patterns(text)
        
        return entities
    
    def extract_patterns(self, text):
        """Extract entities using simple patterns."""
        entities = []
        
        # Extract capitalized words (potential names/places)
        words = text.split()
        for word in words:
            if word.isalpha() and word[0].isupper() and len(word) > 2:
                entities.append(word)
        
        return entities


class ResponseGenerator:
    """Generate various types of responses."""
    
    def __init__(self):
        self.fallback_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "That's interesting! Tell me more about it.",
            "I'm still learning about that topic. Can you explain it differently?",
            "Hmm, I'm not familiar with that. Could you provide more context?",
            "I'd love to help, but I need more information to understand what you mean.",
            "That's a unique perspective! Can you elaborate?",
        ]
    
    def generate_fallback_response(self, text):
        """Generate fallback response for unknown inputs."""
        return random.choice(self.fallback_responses)


class ConversationManager:
    """Manage chatbot conversations and interactions."""
    
    def __init__(self):
        self.chatbot = NLPChatbot()
        self.session_start = datetime.now()
        
    def start_conversation(self):
        """Start interactive conversation with the chatbot."""
        print("🤖 NLP Chatbot Ready!")
        print("=" * 50)
        print("Hi! I'm an AI chatbot with natural language processing capabilities.")
        print("I can understand intents, analyze sentiment, and have meaningful conversations.")
        print("Type 'quit', 'exit', or 'bye' to end our conversation.")
        print("Type 'help' for more information about my capabilities.")
        print("-" * 50)
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                self.end_conversation()
                break
            
            # Special commands
            if user_input.lower() == 'summary':
                self.show_conversation_summary()
                continue
            
            if user_input.lower() == 'help':
                self.show_help()
                continue
            
            # Process message and get response
            try:
                response, intent = self.chatbot.process_message(user_input)
                
                # Show response with optional intent info
                print(f"\nBot: {response}")
                
                # Show sentiment if significantly positive or negative
                sentiment = self.chatbot.sentiment_analyzer.analyze(user_input)
                if abs(sentiment) > 0.3:
                    sentiment_label = self.chatbot.sentiment_analyzer.get_sentiment_label(sentiment)
                    print(f"💭 (I detect a {sentiment_label} sentiment)")
                
            except Exception as e:
                print(f"\nBot: I'm sorry, I encountered an error processing that. Could you try again?")
                print(f"Debug: {e}")
    
    def show_help(self):
        """Show help information."""
        print("\n🛠️ Chatbot Capabilities:")
        print("• Intent Recognition - I can understand what you want to achieve")
        print("• Sentiment Analysis - I can detect emotions in your messages")
        print("• Entity Extraction - I can identify names, places, and objects")
        print("• Context Awareness - I remember our conversation history")
        print("• Knowledge Base - I have information on various topics")
        print("\n💬 Special Commands:")
        print("• 'summary' - View conversation statistics")
        print("• 'help' - Show this help message")
        print("• 'quit/exit/bye' - End conversation")
    
    def show_conversation_summary(self):
        """Display conversation summary."""
        summary = self.chatbot.get_conversation_summary()
        
        print("\n📊 Conversation Summary:")
        print(f"• Total exchanges: {summary['total_exchanges']}")
        print(f"• Average sentiment: {summary['avg_sentiment']:.2f}")
        print(f"• Topics discussed: {', '.join(summary['topics_discussed'])}")
        print(f"• Session duration: {datetime.now() - self.session_start}")
    
    def end_conversation(self):
        """End conversation and show summary."""
        print("\n👋 Thank you for chatting with me!")
        self.show_conversation_summary()
        print("\nHave a great day! 🌟")


def demo_nlp_features():
    """Demonstrate NLP features of the chatbot."""
    print("🔬 NLP Features Demo")
    print("=" * 30)
    
    chatbot = NLPChatbot()
    
    test_messages = [
        "Hello, how are you today?",
        "I'm feeling really sad about my project",
        "Can you help me with Python programming?",
        "What do you know about machine learning?",
        "You're an amazing chatbot!",
        "I'm working on a project with John in New York"
    ]
    
    for message in test_messages:
        print(f"\nInput: {message}")
        
        # Intent prediction
        intent = chatbot.predict_intent(message)
        print(f"Intent: {intent}")
        
        # Sentiment analysis
        sentiment = chatbot.sentiment_analyzer.analyze(message)
        sentiment_label = chatbot.sentiment_analyzer.get_sentiment_label(sentiment)
        print(f"Sentiment: {sentiment_label} ({sentiment:.2f})")
        
        # Entity extraction
        entities = chatbot.entity_extractor.extract(message)
        print(f"Entities: {entities if entities else 'None'}")
        
        # Generate response
        response, _ = chatbot.process_message(message)
        print(f"Response: {response}")
        print("-" * 30)


def main():
    """Main function to run the NLP chatbot."""
    print("🧠 Advanced NLP Chatbot")
    print("=" * 30)
    
    mode = input("Choose mode:\n1. Interactive Chat\n2. NLP Demo\nEnter choice (1/2): ").strip()
    
    if mode == '2':
        demo_nlp_features()
    else:
        manager = ConversationManager()
        manager.start_conversation()


if __name__ == "__main__":
    main()
