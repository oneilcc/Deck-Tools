#!/usr/bin/env python3
"""
Topic and Entity Extraction

Extracts topics, keywords, and entities from presentation text.
"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter
from dataclasses import dataclass
import string


@dataclass
class Topic:
    """Represents an extracted topic."""
    name: str
    relevance_score: float
    keywords: List[str]


@dataclass
class Entity:
    """Represents an extracted entity."""
    name: str
    entity_type: str  # PERSON, ORG, PRODUCT, TECH, etc.
    context: str
    frequency: int


@dataclass
class Keyword:
    """Represents an important keyword."""
    term: str
    frequency: int
    tf_idf_score: float = 0.0


# Common stop words
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
    'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'just', 'slide', 'presentation'
}

# Technology-related terms (customize for your domain)
TECH_KEYWORDS = {
    'api', 'cloud', 'kubernetes', 'docker', 'aws', 'azure', 'gcp',
    'microservices', 'serverless', 'database', 'sql', 'nosql',
    'machine learning', 'ml', 'ai', 'artificial intelligence',
    'devops', 'cicd', 'ci/cd', 'automation', 'infrastructure',
    'security', 'authentication', 'authorization', 'encryption',
    'performance', 'scalability', 'monitoring', 'observability'
}


def clean_text(text: str) -> str:
    """Clean text for processing."""
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove special characters but keep spaces and hyphens
    text = re.sub(r'[^\w\s\-]', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_keywords(text: str, top_n: int = 20) -> List[Keyword]:
    """
    Extract important keywords using frequency analysis.

    Args:
        text: Input text
        top_n: Number of top keywords to return

    Returns:
        List of Keyword objects
    """
    cleaned = clean_text(text)

    # Tokenize
    words = cleaned.split()

    # Filter out stop words and short words
    words = [w for w in words if w not in STOP_WORDS and len(w) > 3]

    # Also extract important phrases (2-3 word combinations)
    phrases = []
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        phrases.append(bigram)

    for i in range(len(words) - 2):
        trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
        phrases.append(trigram)

    # Count frequencies
    word_counts = Counter(words)
    phrase_counts = Counter(phrases)

    # Combine and sort
    all_terms = []

    for term, count in word_counts.most_common(top_n):
        all_terms.append(Keyword(term=term, frequency=count))

    for term, count in phrase_counts.most_common(top_n // 2):
        # Only include phrases that appear multiple times
        if count > 1:
            all_terms.append(Keyword(term=term, frequency=count))

    # Sort by frequency
    all_terms.sort(key=lambda k: k.frequency, reverse=True)

    return all_terms[:top_n]


def extract_tech_terms(text: str) -> Set[str]:
    """Extract technology-related terms."""
    cleaned = clean_text(text)
    found_terms = set()

    for tech_term in TECH_KEYWORDS:
        if tech_term in cleaned:
            found_terms.add(tech_term)

    return found_terms


def extract_capitalized_entities(text: str, min_frequency: int = 2) -> List[Entity]:
    """
    Extract entities based on capitalization patterns.
    Simple heuristic-based extraction.
    """
    # Find sequences of capitalized words
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    matches = re.findall(pattern, text)

    # Count frequencies
    entity_counts = Counter(matches)

    entities = []
    for name, freq in entity_counts.items():
        if freq >= min_frequency and len(name) > 3:
            # Classify entity type based on patterns
            entity_type = classify_entity_type(name)

            entities.append(Entity(
                name=name,
                entity_type=entity_type,
                context="",  # Would need more context for this
                frequency=freq
            ))

    return entities


def classify_entity_type(name: str) -> str:
    """Classify entity type based on patterns."""
    name_lower = name.lower()

    # Check for technology/product indicators
    tech_indicators = ['api', 'server', 'cloud', 'app', 'platform', 'service']
    if any(indicator in name_lower for indicator in tech_indicators):
        return 'TECH'

    # Check for organization indicators
    org_indicators = ['inc', 'corp', 'ltd', 'llc', 'company']
    if any(indicator in name_lower for indicator in org_indicators):
        return 'ORG'

    # Default classifications
    if len(name.split()) == 1:
        return 'PRODUCT'  # Single capitalized words often products
    else:
        return 'ORG'  # Multi-word capitalized phrases often organizations


def extract_topics_from_keywords(keywords: List[Keyword], top_n: int = 10) -> List[Topic]:
    """
    Generate topics from extracted keywords.
    Groups related keywords into topics.
    """
    topics = []

    # For now, use top keywords as individual topics
    # In a more sophisticated system, we'd cluster related keywords
    for i, keyword in enumerate(keywords[:top_n]):
        topic = Topic(
            name=keyword.term.title(),
            relevance_score=keyword.frequency / max(k.frequency for k in keywords) if keywords else 0,
            keywords=[keyword.term]
        )
        topics.append(topic)

    return topics


def analyze_presentation_content(text: str) -> Dict:
    """
    Complete analysis of presentation content.

    Args:
        text: Full presentation text

    Returns:
        Dictionary with keywords, topics, entities, and tech terms
    """
    # Extract keywords
    keywords = extract_keywords(text, top_n=30)

    # Extract topics
    topics = extract_topics_from_keywords(keywords, top_n=10)

    # Extract entities
    entities = extract_capitalized_entities(text, min_frequency=2)

    # Extract tech terms
    tech_terms = extract_tech_terms(text)

    return {
        'keywords': keywords,
        'topics': topics,
        'entities': entities,
        'tech_terms': list(tech_terms)
    }


def main():
    """Test the extraction."""
    sample_text = """
    Introduction to Cloud Native Architecture

    Cloud native applications are designed specifically for cloud environments.
    They leverage microservices, containers, and orchestration platforms like Kubernetes.

    Key Technologies:
    - Docker for containerization
    - Kubernetes for orchestration
    - AWS, Azure, or GCP for cloud infrastructure
    - Prometheus for monitoring
    - GitLab CI/CD for automation

    Benefits:
    - Improved scalability
    - Better resource utilization
    - Faster deployment cycles
    - Enhanced reliability

    Amazon Web Services provides extensive cloud services.
    Microsoft Azure offers enterprise solutions.
    Google Cloud Platform focuses on data and ML.
    """

    result = analyze_presentation_content(sample_text)

    print("=== Keywords ===")
    for kw in result['keywords'][:10]:
        print(f"  {kw.term}: {kw.frequency}")

    print("\n=== Topics ===")
    for topic in result['topics'][:5]:
        print(f"  {topic.name} (score: {topic.relevance_score:.2f})")

    print("\n=== Entities ===")
    for entity in result['entities']:
        print(f"  {entity.name} ({entity.entity_type}): {entity.frequency}")

    print("\n=== Tech Terms ===")
    for term in result['tech_terms']:
        print(f"  {term}")


if __name__ == '__main__':
    main()
