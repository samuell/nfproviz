import argparse
import json
import subprocess as sub

argp = argparse.ArgumentParser()
argp.add_argument(
    "--input", "-i", help="The input BCO file in JSON format", required=True
)
argp.add_argument(
    "--short",
    "-s",
    help="Use shortened paths for filenames for easier overall visibility",
    action="store_true",
)
argp.add_argument(
    "--super-short",
    "-ss",
    help="Use even more shortened paths for filenames for easier overall visibility",
    action="store_true",
)
argp.add_argument(
    "--horizontal-graph",
    "-hg",
    help="Print graph horizontally",
    action="store_true",
)
argp.add_argument("--output", "-o", metavar="Output file in HTML format", required=True)
args = argp.parse_args()


def main():
    with open(args.input) as bco_file:
        bco = json.load(bco_file)
        steps = bco["description_domain"]["pipeline_steps"]
        write_html_report(steps, args.output)


def write_html_report(steps, html_path):
    if html_path[-4:] != "html":
        raise Exception("Html report filename must end with .html")
    dot = generate_dot_graph(steps)
    dot_path = html_path.replace(".html", ".dot")
    svg_path = dot_path.replace(".dot", ".svg")

    with open(dot_path, "w") as dotfile:
        dotfile.write(dot)

    sub.run(f"dot -Tsvg {dot_path} > {svg_path}", shell=True)

    with open(svg_path) as svg_file:
        svg = svg_file.read().strip()

    html = "<html>\n"
    html += "<body style='font-family:monospace, courier new'>\n"
    html += "<h1>Provenance DAG<h1>\n"
    html += "<hr>\n"
    html += "<table borders='none' cellpadding='8px'>\n"
    html += "<tr><th>Start time</th><th>Command</th><th>Duration</th></tr>\n"
    for step in steps:
        html += f"<tr><td style='background: #efefef;'>{step['name']} / {step['description']}</td></tr>\n"
    html += "</table>"
    html += "<hr>"
    html += svg + "\n"
    html += "<hr>\n"
    html += "</body>\n"
    html += "</html>\n"

    with open(html_path, "w") as htmlfile:
        htmlfile.write(html)

    # Open html file in browser
    print(f"Trying to open HTML file in browser: {html_path} ...")
    sub.run(f"open {html_path}", shell=True)


def generate_dot_graph(steps):
    step_nodes, file_nodes, edges = generate_graph(steps)

    dot = "DIGRAPH G {\n"
    if args.horizontal_graph:
        dot += '  rankdir="LR"\n'
    dot += "  node [shape=box, style=filled, fontname=monospace, penwidth=0];"
    for node in step_nodes:
        dot += f' "{node}" [fillcolor=pink]\n'
    for node in file_nodes:
        dot += f' "{node}" [fillcolor=lightblue]\n'
    for edge in edges:
        dot += f'  "{edge[0]}" -> "{edge[1]}"\n'
    dot += "}"

    return dot


def generate_graph(pipeline_steps):
    step_nodes = []
    file_nodes = []
    edges = []
    pipeline_steps.sort(key=lambda x: x["step_number"])
    for step in pipeline_steps:
        node_name = f"{step['name']}"
        if args.short:
            node_name = f"{step['description']} / {step['name'][0:6]}"
        if args.super_short:
            node_name = f"{step['description']}"
        step_nodes.append(node_name)
        for inpath in step["input_list"]:
            parts = inpath.split("/")
            if args.short and inpath.startswith("/work"):
                if len(parts) > 1:
                    parts[-2] = parts[-2][:6]
                inpath = "/".join(parts)
            if args.super_short and inpath.startswith("/work"):
                inpath = parts[-1]
            file_nodes.append(inpath)
            edges.append((inpath, node_name))
        for outpath in step["output_list"]:
            parts = outpath.split("/")
            if args.short and outpath.startswith("/work"):
                if len(parts) > 1:
                    parts[-2] = parts[-2][:6]
                outpath = "/".join(parts)
            if args.super_short and outpath.startswith("/work"):
                outpath = parts[-1]
            file_nodes.append(outpath)
            edges.append((node_name, outpath))
    step_nodes = set(step_nodes)
    file_nodes = set(file_nodes)
    edges = set(edges)
    return step_nodes, file_nodes, edges


if __name__ == "__main__":
    main()
