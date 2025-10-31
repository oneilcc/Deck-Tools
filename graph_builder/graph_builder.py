#!/usr/bin/env python3
"""
Memgraph Graph Builder

Builds a knowledge graph from extracted presentation data.
"""

from gqlalchemy import Memgraph, Node, Relationship, Field
from typing import List, Dict
from dataclasses import dataclass
import os
from pathlib import Path

from pdf_extractor import Presentation, Slide
from topic_extractor import analyze_presentation_content, Keyword, Topic, Entity


# Graph Node Models
class PresentationNode(Node):
    """Presentation node in the graph."""
    filename: str = Field(index=True, unique=True)
    title: str = Field(index=True)
    filepath: str
    total_slides: int
    metadata: Dict = Field(default_factory=dict)


class SlideNode(Node):
    """Slide node in the graph."""
    presentation_filename: str = Field(index=True)
    slide_number: int = Field(index=True)
    title: str = Field(index=True, nullable=True)
    content: str
    slide_id: str = Field(index=True, unique=True)  # presentation_filename:slide_number


class TopicNode(Node):
    """Topic node in the graph."""
    name: str = Field(index=True, unique=True)
    total_mentions: int = Field(default=0)


class KeywordNode(Node):
    """Keyword node in the graph."""
    term: str = Field(index=True, unique=True)
    total_frequency: int = Field(default=0)


class EntityNode(Node):
    """Entity node in the graph."""
    name: str = Field(index=True, unique=True)
    entity_type: str = Field(index=True)
    total_mentions: int = Field(default=0)


# Graph Relationships
class Contains(Relationship, type="CONTAINS"):
    """Presentation contains slide."""
    pass


class Mentions(Relationship, type="MENTIONS"):
    """Slide mentions topic."""
    relevance_score: float = Field(default=0.0)


class ContainsKeyword(Relationship, type="CONTAINS_KEYWORD"):
    """Slide contains keyword."""
    frequency: int = Field(default=1)


class References(Relationship, type="REFERENCES"):
    """Slide references entity."""
    frequency: int = Field(default=1)


class Covers(Relationship, type="COVERS"):
    """Presentation covers topic."""
    total_mentions: int = Field(default=0)


class RelatedTo(Relationship, type="RELATED_TO"):
    """Topic related to another topic."""
    strength: float = Field(default=0.0)


class AssociatedWith(Relationship, type="ASSOCIATED_WITH"):
    """Entity associated with topic."""
    pass


class GraphBuilder:
    """Builds knowledge graph in Memgraph from presentation data."""

    def __init__(self, host: str = "127.0.0.1", port: int = 7687,
                 username: str = "", password: str = ""):
        """
        Initialize connection to Memgraph.

        Args:
            host: Memgraph host
            port: Memgraph port
            username: Memgraph username
            password: Memgraph password
        """
        self.memgraph = Memgraph(host=host, port=port, username=username, password=password)
        print(f"Connected to Memgraph at {host}:{port}")

    def clear_database(self):
        """Clear all nodes and relationships."""
        self.memgraph.execute("MATCH (n) DETACH DELETE n;")
        print("Database cleared")

    def create_indexes(self):
        """Create indexes for better query performance."""
        queries = [
            "CREATE INDEX ON :PresentationNode(filename);",
            "CREATE INDEX ON :PresentationNode(title);",
            "CREATE INDEX ON :SlideNode(slide_id);",
            "CREATE INDEX ON :SlideNode(presentation_filename);",
            "CREATE INDEX ON :TopicNode(name);",
            "CREATE INDEX ON :KeywordNode(term);",
            "CREATE INDEX ON :EntityNode(name);",
            "CREATE INDEX ON :EntityNode(entity_type);",
        ]

        for query in queries:
            try:
                self.memgraph.execute(query)
            except Exception as e:
                # Index might already exist
                pass

        print("Indexes created")

    def load_presentation(self, presentation: Presentation) -> None:
        """
        Load a presentation and its slides into the graph.

        Args:
            presentation: Presentation object to load
        """
        print(f"Loading: {presentation.filename}")

        # Combine all slide content for document-level analysis
        full_text = "\n\n".join(slide.content for slide in presentation.slides)

        # Analyze content
        analysis = analyze_presentation_content(full_text)

        # Create presentation node
        pres_node = PresentationNode(
            filename=presentation.filename,
            title=presentation.title,
            filepath=presentation.filepath,
            total_slides=presentation.total_slides,
            metadata=presentation.metadata
        ).save(self.memgraph)

        # Track document-level topics for the presentation
        doc_topics = {}

        # Create slide nodes and relationships
        for slide in presentation.slides:
            slide_id = f"{presentation.filename}:{slide.slide_number}"

            # Create slide node
            slide_node = SlideNode(
                presentation_filename=presentation.filename,
                slide_number=slide.slide_number,
                title=slide.title,
                content=slide.content,
                slide_id=slide_id
            ).save(self.memgraph)

            # Create CONTAINS relationship
            Contains(_start_node_id=pres_node._id, _end_node_id=slide_node._id).save(self.memgraph)

            # Analyze slide-level content
            slide_analysis = analyze_presentation_content(slide.content)

            # Add topics
            for topic in slide_analysis['topics'][:5]:  # Top 5 topics per slide
                topic_node = self._get_or_create_topic(topic.name)

                # Create MENTIONS relationship
                Mentions(
                    _start_node_id=slide_node._id,
                    _end_node_id=topic_node._id,
                    relevance_score=topic.relevance_score
                ).save(self.memgraph)

                # Track for document level
                doc_topics[topic.name] = doc_topics.get(topic.name, 0) + 1

            # Add keywords
            for keyword in slide_analysis['keywords'][:10]:  # Top 10 keywords per slide
                keyword_node = self._get_or_create_keyword(keyword.term)

                ContainsKeyword(
                    _start_node_id=slide_node._id,
                    _end_node_id=keyword_node._id,
                    frequency=keyword.frequency
                ).save(self.memgraph)

            # Add entities
            for entity in slide_analysis['entities']:
                entity_node = self._get_or_create_entity(entity.name, entity.entity_type)

                References(
                    _start_node_id=slide_node._id,
                    _end_node_id=entity_node._id,
                    frequency=entity.frequency
                ).save(self.memgraph)

        # Create presentation-level COVERS relationships
        for topic_name, mention_count in doc_topics.items():
            topic_node = self._get_or_create_topic(topic_name)

            Covers(
                _start_node_id=pres_node._id,
                _end_node_id=topic_node._id,
                total_mentions=mention_count
            ).save(self.memgraph)

        print(f"  ✓ Loaded {len(presentation.slides)} slides")

    def _get_or_create_topic(self, name: str) -> TopicNode:
        """Get or create a topic node."""
        result = list(self.memgraph.execute_and_fetch(
            "MATCH (t:TopicNode {name: $name}) RETURN t",
            {"name": name}
        ))

        if result:
            topic = TopicNode(**result[0]['t']._properties)
            topic._id = result[0]['t']._id
            # Update mention count
            topic.total_mentions += 1
            topic.save(self.memgraph)
            return topic
        else:
            return TopicNode(name=name, total_mentions=1).save(self.memgraph)

    def _get_or_create_keyword(self, term: str) -> KeywordNode:
        """Get or create a keyword node."""
        result = list(self.memgraph.execute_and_fetch(
            "MATCH (k:KeywordNode {term: $term}) RETURN k",
            {"term": term}
        ))

        if result:
            keyword = KeywordNode(**result[0]['k']._properties)
            keyword._id = result[0]['k']._id
            keyword.total_frequency += 1
            keyword.save(self.memgraph)
            return keyword
        else:
            return KeywordNode(term=term, total_frequency=1).save(self.memgraph)

    def _get_or_create_entity(self, name: str, entity_type: str) -> EntityNode:
        """Get or create an entity node."""
        result = list(self.memgraph.execute_and_fetch(
            "MATCH (e:EntityNode {name: $name}) RETURN e",
            {"name": name}
        ))

        if result:
            entity = EntityNode(**result[0]['e']._properties)
            entity._id = result[0]['e']._id
            entity.total_mentions += 1
            entity.save(self.memgraph)
            return entity
        else:
            return EntityNode(name=name, entity_type=entity_type, total_mentions=1).save(self.memgraph)

    def create_topic_relationships(self):
        """
        Create RELATED_TO relationships between topics that appear together.
        """
        print("Creating topic relationships...")

        query = """
        MATCH (s:SlideNode)-[:MENTIONS]->(t1:TopicNode)
        MATCH (s)-[:MENTIONS]->(t2:TopicNode)
        WHERE t1.name < t2.name
        WITH t1, t2, COUNT(s) as co_occurrences
        WHERE co_occurrences > 1
        MERGE (t1)-[r:RELATED_TO]-(t2)
        SET r.strength = co_occurrences
        RETURN count(r) as relationships_created
        """

        result = list(self.memgraph.execute_and_fetch(query))
        count = result[0]['relationships_created'] if result else 0
        print(f"  ✓ Created {count} topic relationships")

    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        stats = {}

        queries = {
            'presentations': "MATCH (p:PresentationNode) RETURN count(p) as count",
            'slides': "MATCH (s:SlideNode) RETURN count(s) as count",
            'topics': "MATCH (t:TopicNode) RETURN count(t) as count",
            'keywords': "MATCH (k:KeywordNode) RETURN count(k) as count",
            'entities': "MATCH (e:EntityNode) RETURN count(e) as count",
        }

        for name, query in queries.items():
            result = list(self.memgraph.execute_and_fetch(query))
            stats[name] = result[0]['count'] if result else 0

        return stats


def main():
    """Command-line interface."""
    import argparse
    from pdf_extractor import extract_from_directory, extract_slides_from_pdf

    parser = argparse.ArgumentParser(description='Build knowledge graph from PDF presentations')
    parser.add_argument('input', help='PDF file or directory')
    parser.add_argument('--host', default='127.0.0.1', help='Memgraph host')
    parser.add_argument('--port', type=int, default=7687, help='Memgraph port')
    parser.add_argument('--clear', action='store_true', help='Clear database before loading')
    parser.add_argument('-r', '--recursive', action='store_true', help='Process subdirectories')

    args = parser.parse_args()

    # Connect to Memgraph
    builder = GraphBuilder(host=args.host, port=args.port)

    if args.clear:
        builder.clear_database()

    builder.create_indexes()

    # Extract presentations
    input_path = Path(args.input)
    if input_path.is_file():
        presentations = [extract_slides_from_pdf(input_path)]
    else:
        presentations = extract_from_directory(input_path, args.recursive)

    # Load into graph
    print(f"\nLoading {len(presentations)} presentations into graph...")
    for presentation in presentations:
        builder.load_presentation(presentation)

    # Create topic relationships
    builder.create_topic_relationships()

    # Print statistics
    stats = builder.get_statistics()
    print(f"\n{'='*60}")
    print("Graph Statistics:")
    for name, count in stats.items():
        print(f"  {name.title()}: {count}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
