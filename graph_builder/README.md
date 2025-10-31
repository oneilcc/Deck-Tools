# Conference Knowledge Graph Builder

Build a knowledge graph from PDF slide decks using Memgraph. Perfect for conference preparation, agenda planning, and blog post generation.

## Overview

This tool extracts content from PDF presentations and builds a graph database with:
- **Presentations** and **Slides** as structural nodes
- **Topics** and **Keywords** extracted from content
- **Entities** (people, organizations, technologies)
- **Relationships** showing how concepts connect across presentations

## Use Cases

1. **Agenda Planning**: Identify popular topics and organize tracks
2. **Pre-Conference Blog Posts**: Find trending themes and create preview content
3. **Post-Conference Content**: Query the graph to find connections and insights
4. **Knowledge Discovery**: Explore relationships between presentations

## Prerequisites

1. **Memgraph** running in Docker:
   ```bash
   docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
   ```

2. **Python 3.8+**

3. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

###  1. Build the Graph

Process all PDFs in a directory and load them into Memgraph:

```bash
cd graph_builder

# Load presentations from your TechCON folder
python graph_builder.py "/Users/colin/Documents/TechCON/2025 - Dallas" --recursive --clear

# This will:
# - Extract text from all PDFs
# - Analyze content for topics, keywords, and entities
# - Load everything into Memgraph
# - Create relationships between concepts
```

### 2. Generate Agenda Suggestions

Get AI-assisted agenda recommendations based on content analysis:

```bash
python query_tools.py --action agenda
```

Output example:
```
=== Agenda Suggestions ===

KEYNOTE TOPICS:
  - Cloud Architecture (15 presentations, 145 mentions)
  - Machine Learning (12 presentations, 98 mentions)
  - DevOps (10 presentations, 87 mentions)

SUGGESTED TRACKS:
Track 1: Cloud Architecture
  Related: Kubernetes, Microservices, Scalability
  Presentations: 15

Track 2: Machine Learning
  Related: AI, Data Science, Neural Networks
  Presentations: 12
```

### 3. Query for Blog Post Material

Get content for writing about a specific topic:

```bash
python query_tools.py --action search --query "kubernetes"
```

### 4. Explore Topics

See what topics are covered across all presentations:

```bash
python query_tools.py --action topics
```

## Architecture

```
PDF Slide Decks
    ↓
Text Extraction (pdfplumber)
    ↓
NLP Analysis (topic_extractor.py)
    ↓
Graph Database (Memgraph)
    ↓
Query Tools (query_tools.py)
```

## Graph Schema

### Nodes

- **PresentationNode**: PDF documents
  - `filename`, `title`, `filepath`, `total_slides`, `metadata`

- **SlideNode**: Individual slides
  - `slide_id`, `slide_number`, `title`, `content`

- **TopicNode**: Extracted themes/subjects
  - `name`, `total_mentions`

- **KeywordNode**: Important terms
  - `term`, `total_frequency`

- **EntityNode**: People, organizations, products, technologies
  - `name`, `entity_type`, `total_mentions`

### Relationships

- `Presentation -[CONTAINS]-> Slide`
- `Presentation -[COVERS]-> Topic`
- `Slide -[MENTIONS]-> Topic`
- `Slide -[CONTAINS_KEYWORD]-> Keyword`
- `Slide -[REFERENCES]-> Entity`
- `Topic -[RELATED_TO]-> Topic`

## Usage Examples

### Extract Text Only

Test extraction without loading into database:

```bash
python pdf_extractor.py "/path/to/presentation.pdf" -o output.json
```

### Test Topic Extraction

```bash
python topic_extractor.py
```

### Get Presentation Summary

```bash
python query_tools.py --action summary --query "presentation.pdf"
```

### Find Related Presentations

Use the Python API:

```python
from query_tools import ConferenceQueryTools

tools = ConferenceQueryTools()

# Find presentations similar to a specific one
related = tools.find_related_presentations("my_presentation.pdf", limit=5)

for pres in related:
    print(f"{pres['title']}: {pres['similarity']} shared topics")
```

### Generate Blog Post Material

```python
from query_tools import ConferenceQueryTools

tools = ConferenceQueryTools()

# Get material for a blog post about "Cloud Native"
material = tools.get_blog_post_material("Cloud Native")

print(f"Topic: {material['topic']}")
print(f"Related: {', '.join(material['related_topics'])}")
print(f"Presentations covering this: {len(material['presentations'])}")

for pres in material['presentations']:
    print(f"  - {pres['title']}")
    print(f"    Keywords: {', '.join(pres['keywords'][:5])}")
```

## Workflow for Conference Preparation

### Phase 1: Pre-Conference (Agenda Planning)

1. **Load all presentations**:
   ```bash
   python graph_builder.py "/path/to/presentations" --recursive --clear
   ```

2. **Generate agenda suggestions**:
   ```bash
   python query_tools.py --action agenda > agenda_suggestions.txt
   ```

3. **Explore top topics**:
   ```bash
   python query_tools.py --action topics
   ```

4. **Write preview blog posts** using topic analysis

### Phase 2: During Conference

- Use search to quickly find related presentations
- Query for on-the-fly content connections

### Phase 3: Post-Conference (Blog Writing)

1. **Query for specific topics**:
   ```bash
   python query_tools.py --action search --query "your_topic"
   ```

2. **Get comprehensive material**:
   ```python
   tools = ConferenceQueryTools()
   material = tools.get_blog_post_material("Kubernetes")
   # Use material to write blog post
   ```

3. **Find connections** between presentations for insightful content

## Advanced Queries

You can run custom Cypher queries directly:

```python
from gqlalchemy import Memgraph

memgraph = Memgraph()

# Find presentations with most unique topics
query = """
MATCH (p:PresentationNode)-[:COVERS]->(t:TopicNode)
WITH p, count(DISTINCT t) as topic_count
RETURN p.title, topic_count
ORDER BY topic_count DESC
LIMIT 10
"""

results = list(memgraph.execute_and_fetch(query))
for r in results:
    print(f"{r['p.title']}: {r['topic_count']} topics")
```

## Customization

### Adding Custom Entity Types

Edit `topic_extractor.py` and add domain-specific patterns:

```python
TECH_KEYWORDS = {
    'your', 'custom', 'terms', 'here'
}
```

### Adjusting Topic Extraction

Modify `extract_keywords()` in `topic_extractor.py` to change:
- Number of keywords extracted
- Stop words list
- Phrase patterns (bigrams, trigrams)

### Custom Relationships

Add new relationship types in `graph_builder.py`:

```python
class CustomRelationship(Relationship, type="CUSTOM_TYPE"):
    """Your custom relationship."""
    pass
```

## Troubleshooting

**Can't connect to Memgraph:**
- Ensure Docker container is running: `docker ps`
- Check ports: 7687 (Bolt), 7444 (HTTP)

**Low-quality topic extraction:**
- Add more domain-specific keywords to `TECH_KEYWORDS`
- Adjust `STOP_WORDS` to filter out noise
- Increase `top_n` parameter in keyword extraction

**Memory issues with large PDFs:**
- Process in batches
- Don't use `--clear` flag to keep existing data

## Next Steps

1. **Visualize the graph**: Use Memgraph Lab (http://localhost:7444) to explore visually
2. **Enhance entity extraction**: Integrate spaCy or transformers for better NLP
3. **Add semantic search**: Use embeddings for similarity matching
4. **Export insights**: Generate reports, visualizations, or presentations

## Files

- `requirements.txt` - Python dependencies
- `pdf_extractor.py` - Extract text from PDFs
- `topic_extractor.py` - NLP analysis for topics/keywords/entities
- `graph_builder.py` - Load data into Memgraph
- `query_tools.py` - Query utilities for agenda and blog posts
- `README.md` - This file

## License

Part of Deck-Tools project
