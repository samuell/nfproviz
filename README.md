# nfproviz
A small tool to parse experimental BioObject Component output from Nextlfow

## Requirements

- Python 3.6+ (Needs to support f-strings)
- The [GraphViz](https://graphviz.org/) dot command, for generating the graph.

## Installation

```bash
git clone https://github.com/samuell/nfproviz.git
cd nfproviz
```

## Usage

```bash
python nfproviz.py -i bco.json -o bco.html
```

For shortened step/file paths:

```bash
python nfproviz.py -s -i bco.json -o bco.html
```

For even more shortened step/file paths:

```bash
python nfproviz.py -ss -i bco.json -o bco.html
```

For horizontal graph:

```bash
python nfproviz.py -hg -i bco.json -o bco.html
```
