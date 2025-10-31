"""
Conference Knowledge Graph Builder

Build knowledge graphs from PDF slide decks for conference preparation and analysis.
"""

__version__ = "1.0.0"

from .pdf_extractor import extract_slides_from_pdf, extract_from_directory, Presentation, Slide
from .topic_extractor import analyze_presentation_content, Topic, Entity, Keyword
from .graph_builder import GraphBuilder
from .query_tools import ConferenceQueryTools, PresentationSummary, TopicCluster

__all__ = [
    'extract_slides_from_pdf',
    'extract_from_directory',
    'analyze_presentation_content',
    'GraphBuilder',
    'ConferenceQueryTools',
    'Presentation',
    'Slide',
    'Topic',
    'Entity',
    'Keyword',
    'PresentationSummary',
    'TopicCluster',
]
