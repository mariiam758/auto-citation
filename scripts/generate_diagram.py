import json
import sys
import networkx as nx
import plotly.graph_objects as go

def generate_plotly_graph(input_json_path, output_html_path):
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()

    # Add keyword nodes
    keywords = list(data.keys())
    for keyword in keywords:
        G.add_node(keyword, type='keyword')

    # Add reference nodes
    ref_nodes = []
    for keyword, refs in data.items():
        for i, ref in enumerate(refs):
            ref_id = f"{keyword}_ref_{i}"
            title = ref.get('title', f'Untitled {i}')
            G.add_node(ref_id, label=title, type='ref')
            G.add_edge(keyword, ref_id)
            ref_nodes.append(ref_id)

    # Create positions manually
    pos = {}

    # Place keywords on the left (x=0), spread vertically
    for i, keyword in enumerate(keywords):
        pos[keyword] = (0, -i)  # y negative just for better spacing

    # Place references on the right (x=1), spread vertically
    for i, ref in enumerate(ref_nodes):
        pos[ref] = (1, -i)

    # Then rest of your plotting code stays the same...
    edge_x = []
    edge_y = []
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

    node_x = []
    node_y = []
    node_text = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        if G.nodes[node].get('type') == 'keyword':
            node_color.append('orange')
            node_text.append(node)
        else:
            node_color.append('lightblue')
            node_text.append(G.nodes[node].get('label', ''))

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
                        title='Keyword → Reference Graph',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                   )
    fig.write_html(output_html_path)
    print(f"✅ Interactive Plotly graph saved to: {output_html_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/generate_plotly_graph.py <input_json> <output_html>")
        sys.exit(1)

    generate_plotly_graph(sys.argv[1], sys.argv[2])

# python scripts/generate_diagram.py references_raw/article_1_references_openalex.json diagrams/article_1_openalex_plotly.html