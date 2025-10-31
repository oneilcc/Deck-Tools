#!/usr/bin/env python3
"""
Example Workflow: Conference Knowledge Graph

Demonstrates complete workflow from PDF extraction to blog post generation.
"""

from pathlib import Path
from graph_builder import GraphBuilder
from query_tools import ConferenceQueryTools
from pdf_extractor import extract_from_directory


def main():
    print("="*70)
    print("Conference Knowledge Graph - Example Workflow")
    print("="*70)
    print()

    # Configuration
    PDF_DIRECTORY = "/Users/colin/Documents/TechCON/2025 - Dallas"
    MEMGRAPH_HOST = "127.0.0.1"
    MEMGRAPH_PORT = 7687

    print("Step 1: Extracting content from PDFs...")
    print(f"Directory: {PDF_DIRECTORY}")
    print()

    # Extract presentations
    pdf_path = Path(PDF_DIRECTORY)
    if not pdf_path.exists():
        print(f"❌ Directory not found: {PDF_DIRECTORY}")
        print("   Please update PDF_DIRECTORY in this script.")
        return

    presentations = extract_from_directory(pdf_path, recursive=True)
    print(f"✓ Extracted {len(presentations)} presentations")
    print()

    # Connect to Memgraph and build graph
    print("Step 2: Building knowledge graph in Memgraph...")
    print(f"Connecting to Memgraph at {MEMGRAPH_HOST}:{MEMGRAPH_PORT}")
    print()

    try:
        builder = GraphBuilder(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    except Exception as e:
        print(f"❌ Failed to connect to Memgraph: {e}")
        print("   Make sure Memgraph is running:")
        print("   docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform")
        return

    # Optional: clear database
    print("Clearing existing data...")
    builder.clear_database()

    print("Creating indexes...")
    builder.create_indexes()

    print(f"Loading {len(presentations)} presentations...")
    for presentation in presentations:
        builder.load_presentation(presentation)

    print("\nCreating topic relationships...")
    builder.create_topic_relationships()

    # Get statistics
    stats = builder.get_statistics()
    print()
    print("="*70)
    print("Graph Statistics:")
    print("="*70)
    for name, count in stats.items():
        print(f"  {name.title()}: {count}")
    print("="*70)
    print()

    # Query the graph
    print("Step 3: Querying the knowledge graph...")
    print()

    tools = ConferenceQueryTools(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)

    # Get agenda suggestions
    print("--- Agenda Suggestions ---")
    print()
    agenda = tools.generate_agenda_suggestions()

    print("KEYNOTE TOPICS (based on popularity):")
    for kt in agenda['keynote_topics']:
        print(f"  • {kt['topic']}")
        print(f"    {kt['presentations']} presentations, {kt['mentions']} total mentions")
    print()

    print("SUGGESTED CONFERENCE TRACKS:")
    for i, (track_name, track_info) in enumerate(list(agenda['track_suggestions'].items())[:3], 1):
        print(f"\n{i}. {track_name}")
        print(f"   Related topics: {', '.join(track_info['related_topics'][:3])}")
        print(f"   Number of presentations: {len(track_info['presentations'])}")
        print(f"   Sample presentations:")
        for pres_title in track_info['presentations'][:3]:
            print(f"     - {pres_title}")
    print()
    print("="*70)
    print()

    # Get top topics for blog posts
    print("--- Topics for Blog Posts ---")
    print()
    top_topics = tools.get_top_topics(limit=10)
    print("Most mentioned topics across all presentations:")
    for i, topic in enumerate(top_topics[:10], 1):
        print(f"  {i}. {topic['topic']}")
        print(f"     {topic['mentions']} mentions across {topic['presentation_count']} presentations")
    print()
    print("="*70)
    print()

    # Example: Get material for a blog post
    if top_topics:
        example_topic = top_topics[0]['topic']
        print(f"--- Blog Post Material: '{example_topic}' ---")
        print()

        material = tools.get_blog_post_material(example_topic)

        print(f"Topic: {material['topic']}")
        print()

        if material['related_topics']:
            print(f"Related topics (for context):")
            for rt in material['related_topics'][:5]:
                print(f"  • {rt}")
            print()

        if material['presentations']:
            print(f"Presentations covering this topic:")
            for pres in material['presentations'][:3]:
                print(f"\n  '{pres['title']}'")
                if pres['keywords']:
                    print(f"  Key terms: {', '.join(pres['keywords'][:5])}")
                if pres['entities']:
                    print(f"  Mentions: {', '.join(pres['entities'][:3])}")
            print()

        if material['entities']:
            print(f"Key entities/technologies mentioned:")
            for entity in material['entities'][:5]:
                print(f"  • {entity['name']} ({entity['type']})")
            print()

        print("="*70)
        print()

    # Example: Find related presentations
    if presentations:
        example_pres = presentations[0].filename
        print(f"--- Related Presentations ---")
        print()
        print(f"Presentations related to: {presentations[0].title}")
        print()

        related = tools.find_related_presentations(example_pres, limit=5)
        if related:
            for i, rel in enumerate(related, 1):
                print(f"  {i}. {rel['title']}")
                print(f"     Similarity: {rel['similarity']} shared topics")
        else:
            print("  No related presentations found")

        print()
        print("="*70)
        print()

    # Summary
    print("="*70)
    print("Workflow Complete!")
    print("="*70)
    print()
    print("What you can do now:")
    print()
    print("1. Visualize the graph in Memgraph Lab:")
    print("   Open http://localhost:7444 in your browser")
    print()
    print("2. Query for specific topics:")
    print("   python query_tools.py --action search --query 'your_topic'")
    print()
    print("3. Get presentation summaries:")
    print("   python query_tools.py --action summary --query 'presentation.pdf'")
    print()
    print("4. Use the Python API for custom queries:")
    print("   from query_tools import ConferenceQueryTools")
    print("   tools = ConferenceQueryTools()")
    print("   # Your custom queries here")
    print()
    print("5. Write your blog posts using the extracted insights!")
    print()


if __name__ == '__main__':
    main()
