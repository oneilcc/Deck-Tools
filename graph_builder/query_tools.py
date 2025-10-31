#!/usr/bin/env python3
"""
Query Tools for Conference Knowledge Graph

Provides utilities for agenda generation and blog post preparation.
"""

from gqlalchemy import Memgraph
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PresentationSummary:
    """Summary of a presentation."""
    filename: str
    title: str
    total_slides: int
    top_topics: List[tuple]  # (topic_name, mention_count)
    key_entities: List[str]
    keywords: List[str]


@dataclass
class TopicCluster:
    """Cluster of related topics."""
    main_topic: str
    related_topics: List[str]
    presentations: List[str]
    total_mentions: int


class ConferenceQueryTools:
    """Query tools for conference knowledge graph."""

    def __init__(self, host: str = "127.0.0.1", port: int = 7687):
        """Initialize connection to Memgraph."""
        self.memgraph = Memgraph(host=host, port=port)

    def get_all_presentations(self) -> List[Dict]:
        """Get all presentations with basic info."""
        query = """
        MATCH (p:PresentationNode)
        RETURN p.filename as filename, p.title as title, p.total_slides as total_slides
        ORDER BY p.title
        """

        return list(self.memgraph.execute_and_fetch(query))

    def get_presentation_summary(self, filename: str) -> Optional[PresentationSummary]:
        """
        Get detailed summary of a presentation.

        Args:
            filename: Presentation filename

        Returns:
            PresentationSummary object
        """
        # Get basic info
        basic_query = """
        MATCH (p:PresentationNode {filename: $filename})
        RETURN p.filename as filename, p.title as title, p.total_slides as total_slides
        """

        basic_result = list(self.memgraph.execute_and_fetch(basic_query, {"filename": filename}))
        if not basic_result:
            return None

        basic = basic_result[0]

        # Get top topics
        topics_query = """
        MATCH (p:PresentationNode {filename: $filename})-[c:COVERS]->(t:TopicNode)
        RETURN t.name as topic, c.total_mentions as mentions
        ORDER BY c.total_mentions DESC
        LIMIT 10
        """

        topics = list(self.memgraph.execute_and_fetch(topics_query, {"filename": filename}))
        top_topics = [(t['topic'], t['mentions']) for t in topics]

        # Get entities
        entities_query = """
        MATCH (p:PresentationNode {filename: $filename})-[:CONTAINS]->(s:SlideNode)-[:REFERENCES]->(e:EntityNode)
        RETURN DISTINCT e.name as entity
        LIMIT 10
        """

        entities = list(self.memgraph.execute_and_fetch(entities_query, {"filename": filename}))
        key_entities = [e['entity'] for e in entities]

        # Get keywords
        keywords_query = """
        MATCH (p:PresentationNode {filename: $filename})-[:CONTAINS]->(s:SlideNode)-[:CONTAINS_KEYWORD]->(k:KeywordNode)
        RETURN DISTINCT k.term as keyword
        LIMIT 15
        """

        keywords = list(self.memgraph.execute_and_fetch(keywords_query, {"filename": filename}))
        keyword_list = [k['keyword'] for k in keywords]

        return PresentationSummary(
            filename=basic['filename'],
            title=basic['title'],
            total_slides=basic['total_slides'],
            top_topics=top_topics,
            key_entities=key_entities,
            keywords=keyword_list
        )

    def get_top_topics(self, limit: int = 20) -> List[Dict]:
        """
        Get most mentioned topics across all presentations.

        Args:
            limit: Number of topics to return

        Returns:
            List of topics with mention counts and presentation counts
        """
        query = """
        MATCH (t:TopicNode)
        OPTIONAL MATCH (p:PresentationNode)-[:COVERS]->(t)
        WITH t, t.total_mentions as mentions, count(DISTINCT p) as presentation_count
        RETURN t.name as topic, mentions, presentation_count
        ORDER BY mentions DESC
        LIMIT $limit
        """

        return list(self.memgraph.execute_and_fetch(query, {"limit": limit}))

    def get_presentations_by_topic(self, topic: str) -> List[Dict]:
        """
        Find presentations covering a specific topic.

        Args:
            topic: Topic name

        Returns:
            List of presentations with relevance scores
        """
        query = """
        MATCH (p:PresentationNode)-[c:COVERS]->(t:TopicNode {name: $topic})
        RETURN p.filename as filename, p.title as title, c.total_mentions as relevance
        ORDER BY c.total_mentions DESC
        """

        return list(self.memgraph.execute_and_fetch(query, {"topic": topic}))

    def find_related_presentations(self, filename: str, limit: int = 5) -> List[Dict]:
        """
        Find presentations related to a given presentation based on shared topics.

        Args:
            filename: Source presentation filename
            limit: Number of related presentations to return

        Returns:
            List of related presentations with similarity scores
        """
        query = """
        MATCH (p1:PresentationNode {filename: $filename})-[:COVERS]->(t:TopicNode)<-[:COVERS]-(p2:PresentationNode)
        WHERE p1 <> p2
        WITH p2, count(t) as shared_topics
        RETURN p2.filename as filename, p2.title as title, shared_topics as similarity
        ORDER BY shared_topics DESC
        LIMIT $limit
        """

        return list(self.memgraph.execute_and_fetch(query, {"filename": filename, "limit": limit}))

    def get_topic_clusters(self, min_presentations: int = 2) -> List[TopicCluster]:
        """
        Get clusters of related topics for agenda organization.

        Args:
            min_presentations: Minimum presentations for a cluster

        Returns:
            List of TopicCluster objects
        """
        # Get topics with their connected topics
        query = """
        MATCH (t1:TopicNode)-[r:RELATED_TO]-(t2:TopicNode)
        WITH t1, collect(t2.name) as related, t1.total_mentions as mentions
        WHERE mentions >= $min_presentations
        RETURN t1.name as topic, related, mentions
        ORDER BY mentions DESC
        """

        results = list(self.memgraph.execute_and_fetch(query, {"min_presentations": min_presentations}))

        clusters = []
        for result in results:
            # Get presentations for this topic
            pres_query = """
            MATCH (p:PresentationNode)-[:COVERS]->(t:TopicNode {name: $topic})
            RETURN p.title as title
            """

            presentations = list(self.memgraph.execute_and_fetch(pres_query, {"topic": result['topic']}))
            pres_titles = [p['title'] for p in presentations]

            cluster = TopicCluster(
                main_topic=result['topic'],
                related_topics=result['related'][:5],  # Top 5 related
                presentations=pres_titles,
                total_mentions=result['mentions']
            )
            clusters.append(cluster)

        return clusters

    def generate_agenda_suggestions(self) -> Dict:
        """
        Generate suggested agenda based on topic analysis.

        Returns:
            Dictionary with agenda suggestions organized by theme
        """
        agenda = {
            'keynote_topics': [],
            'track_suggestions': {},
            'popular_topics': []
        }

        # Get top topics for keynotes
        top_topics = self.get_top_topics(limit=10)
        agenda['keynote_topics'] = [
            {
                'topic': t['topic'],
                'presentations': t['presentation_count'],
                'mentions': t['mentions']
            }
            for t in top_topics[:5]
        ]

        # Get topic clusters for tracks
        clusters = self.get_topic_clusters(min_presentations=2)
        for i, cluster in enumerate(clusters[:5], start=1):
            agenda['track_suggestions'][f'Track {i}: {cluster.main_topic}'] = {
                'main_topic': cluster.main_topic,
                'related_topics': cluster.related_topics,
                'presentations': cluster.presentations,
                'audience_interest': cluster.total_mentions
            }

        # Popular topics across the conference
        agenda['popular_topics'] = [t['topic'] for t in top_topics]

        return agenda

    def get_blog_post_material(self, topic: str) -> Dict:
        """
        Get material for writing a blog post about a topic.

        Args:
            topic: Topic to write about

        Returns:
            Dictionary with relevant content
        """
        material = {
            'topic': topic,
            'presentations': [],
            'key_points': [],
            'related_topics': [],
            'entities': []
        }

        # Get presentations covering this topic
        presentations = self.get_presentations_by_topic(topic)
        for pres in presentations[:5]:  # Top 5 most relevant
            summary = self.get_presentation_summary(pres['filename'])
            if summary:
                material['presentations'].append({
                    'title': summary.title,
                    'keywords': summary.keywords[:10],
                    'entities': summary.key_entities
                })

        # Get related topics for context
        related_query = """
        MATCH (t1:TopicNode {name: $topic})-[:RELATED_TO]-(t2:TopicNode)
        RETURN t2.name as related_topic
        LIMIT 10
        """

        related = list(self.memgraph.execute_and_fetch(related_query, {"topic": topic}))
        material['related_topics'] = [r['related_topic'] for r in related]

        # Get key entities mentioned with this topic
        entities_query = """
        MATCH (t:TopicNode {name: $topic})<-[:MENTIONS]-(s:SlideNode)-[:REFERENCES]->(e:EntityNode)
        RETURN DISTINCT e.name as entity, e.entity_type as type
        LIMIT 10
        """

        entities = list(self.memgraph.execute_and_fetch(entities_query, {"topic": topic}))
        material['entities'] = [{'name': e['entity'], 'type': e['type']} for e in entities]

        return material

    def search_presentations(self, keyword: str) -> List[Dict]:
        """
        Search presentations by keyword in title or content.

        Args:
            keyword: Search term

        Returns:
            List of matching presentations
        """
        query = """
        MATCH (p:PresentationNode)-[:CONTAINS]->(s:SlideNode)
        WHERE toLower(p.title) CONTAINS toLower($keyword)
           OR toLower(s.content) CONTAINS toLower($keyword)
        RETURN DISTINCT p.filename as filename, p.title as title, count(s) as matching_slides
        ORDER BY matching_slides DESC
        """

        return list(self.memgraph.execute_and_fetch(query, {"keyword": keyword}))


def main():
    """Interactive query tool."""
    import argparse

    parser = argparse.ArgumentParser(description='Query conference knowledge graph')
    parser.add_argument('--host', default='127.0.0.1', help='Memgraph host')
    parser.add_argument('--port', type=int, default=7687, help='Memgraph port')
    parser.add_argument('--action', choices=['agenda', 'topics', 'search', 'summary'],
                       required=True, help='Action to perform')
    parser.add_argument('--query', help='Search query or filename')

    args = parser.parse_args()

    tools = ConferenceQueryTools(host=args.host, port=args.port)

    if args.action == 'agenda':
        print("=== Agenda Suggestions ===\n")
        agenda = tools.generate_agenda_suggestions()

        print("KEYNOTE TOPICS:")
        for kt in agenda['keynote_topics']:
            print(f"  - {kt['topic']} ({kt['presentations']} presentations, {kt['mentions']} mentions)")

        print("\nSUGGESTED TRACKS:")
        for track_name, track_info in agenda['track_suggestions'].items():
            print(f"\n{track_name}:")
            print(f"  Related: {', '.join(track_info['related_topics'][:3])}")
            print(f"  Presentations: {len(track_info['presentations'])}")

    elif args.action == 'topics':
        print("=== Top Topics ===\n")
        topics = tools.get_top_topics(limit=20)
        for topic in topics:
            print(f"  {topic['topic']}: {topic['mentions']} mentions in {topic['presentation_count']} presentations")

    elif args.action == 'search' and args.query:
        print(f"=== Search Results for '{args.query}' ===\n")
        results = tools.search_presentations(args.query)
        for result in results:
            print(f"  {result['title']}")
            print(f"    ({result['matching_slides']} matching slides)")

    elif args.action == 'summary' and args.query:
        print(f"=== Presentation Summary ===\n")
        summary = tools.get_presentation_summary(args.query)
        if summary:
            print(f"Title: {summary.title}")
            print(f"Slides: {summary.total_slides}")
            print(f"\nTop Topics:")
            for topic, count in summary.top_topics[:5]:
                print(f"  - {topic} ({count} mentions)")
            print(f"\nKeywords: {', '.join(summary.keywords[:10])}")
            print(f"\nEntities: {', '.join(summary.key_entities[:5])}")
        else:
            print("Presentation not found")


if __name__ == '__main__':
    main()
