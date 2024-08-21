import argparse
import json
from jinja2 import Template

parser = argparse.ArgumentParser()
parser.add_argument('template_file', type=str, help='Path to the jinja2 template file')
parser.add_argument('data_file', type=str, help='Path to the file with variables')
parser.add_argument('output_file', type=str, help='Path to the generated output file')

args = parser.parse_args()

with open(args.data_file) as file:
    data = json.load(file)
with open(args.template_file) as file:
    template = Template(file.read())
with open(args.output_file, "w") as file:
    file.write(template.render(data))
