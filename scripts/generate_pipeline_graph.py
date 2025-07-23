import json
import sys
import os
import networkx as nx
import plotly.graph_objects as go

def generate_pipeline_graph(article_path, output_html_path):
    article_base = os.path.splitext(os.path.basename(article_path))[0]

    # Load keywords
    keywords_path = f"keywords/{article_base}_keywords.json"
    if not os.path.exists(keywords_path):
        print(f"Keywords file not found: {keywords_path}")
        sys.exit(1)
    with open(keywords_path, "r", encoding="utf-8") as f:
        keywords_data = json.load(f)

    all_keyword_groups = ["rake", "yake", "bert_score"]
    sources = ["openalex", "semanticscholar", "crossref"]

    # Load all reference files
    references = {group: {source: {} for source in sources} for group in all_keyword_groups}
    for group in all_keyword_groups:
        for source in sources:
            ref_path = f"references_raw/{article_base}_references_{source}_{group}.json"
            if not os.path.exists(ref_path):
                print(f"Warning : Reference file not found: {ref_path}")
                continue
            with open(ref_path, "r", encoding="utf-8") as f:
                references[group][source] = json.load(f)

    G = nx.DiGraph()

    # Add article node
    G.add_node(article_base, label=article_base, type='article', x=0, y=0)

    # Add keyword extractor nodes
    for i, method in enumerate(all_keyword_groups):
        G.add_node(method, label=method, type='method', x=1, y=-i)
        G.add_edge(article_base, method)

    # Add keyword nodes
    for i, method in enumerate(all_keyword_groups):
        kws = keywords_data.get(method, [])
        if kws:
            for j, kw in enumerate(kws):
                kw_node = f"{method}_kw_{j}"
                G.add_node(kw_node, label=kw, type='keyword', x=2, y=-i*5 - j)
                G.add_edge(method, kw_node)
        else:
            placeholder = f"{method}_kw_empty"
            G.add_node(placeholder, label="(no keywords)", type='keyword', x=2, y=-i*5)
            G.add_edge(method, placeholder)

    # Add references and source nodes
    ref_y_counter = 0
    for method in all_keyword_groups:
        kws = keywords_data.get(method, [])
        for kw_idx, kw in enumerate(kws):
            kw_node = f"{method}_kw_{kw_idx}"
            for source in sources:
                ref_data = references[method].get(source, {})
                refs = ref_data.get(kw, [])
                for k, ref in enumerate(refs):
                    ref_id = f"ref_{source}_{method}_{kw_idx}_{k}"
                    ref_title = ref.get("title", f"Ref {k}")
                    G.add_node(ref_id, label=ref_title, type='reference', x=3, y=ref_y_counter)
                    G.add_edge(kw_node, ref_id)
                    G.add_edge(ref_id, source)
                    ref_y_counter -= 1

    # Add source nodes
    for i, source in enumerate(sources):
        G.add_node(source, label=source, type='source', x=4, y=-i*5)

    # Compute positions
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}

    # Edge trace
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Node trace
    node_x, node_y, node_text, node_color = [], [], [], []
    color_map = {
        'article': 'darkgreen',
        'method': 'orange',
        'keyword': 'lightblue',
        'reference': 'purple',
        'source': 'red'
    }

    for node, data in G.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(data.get('label', node))
        node_color.append(color_map.get(data.get('type'), 'gray'))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            color=node_color,
            size=20,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=f'Full Pipeline Graph for {article_base}',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                   )

    fig.write_html(output_html_path)
    print(f"Pipeline graph saved to: {output_html_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/generate_pipeline_graph.py <article_path> <output_html>")
        sys.exit(1)

    generate_pipeline_graph(sys.argv[1], sys.argv[2])

# python scripts/generate_pipeline_graph.py articles/article_1.txt diagrams/article_1_pipeline.html
