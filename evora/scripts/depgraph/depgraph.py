import glob
import os
from graphviz import Digraph
import distutils.sysconfig as sysconfig


imports = []
dot = Digraph()


class pyfile:
    def __init__(self, name, imports):
        self.name = name
        self.imports = imports


# Gets all modules in python's standard library
std_modules = []
std_lib = sysconfig.get_python_lib(standard_lib=True)
for top, dirs, files in os.walk(std_lib):
    for nm in files:
        if nm != '__init__.py' and nm[-3:] == '.py':
            std_modules.append(os.path.join(top, nm)[len(std_lib) + 1:-3].replace(os.sep, '.'))


# Get all lines with imports on them
for file in glob.glob('../*.py'):
    with open(file) as f:
        modules = []
        importlines = []

        for line in f:
            if 'import' in line:
                importlines.append(line)

        # from whatever import something -> whatever
        for importline in importlines:
            modules.append(importline.split(' ')[1].strip().split('.')[0])

        # give pyfile object current filename, modules found above
        imports.append(pyfile(f.name[3:], modules))

# Add a node for every file to a subgraph
with dot.subgraph(name='cluster_0') as m:
    for filename in imports:
        m.node(filename.name)

# Add a node for every module to one of two subgraphs
with dot.subgraph(name='cluster_1') as s, dot.subgraph(
        name='cluster_2') as d:

    existing = []

    for filename in imports:
        for module in filename.imports:
            # Second part needed to filter out comments
            if module not in existing:
                if module in std_modules:
                    s.node(module)
                else:
                    d.node(module)

            existing.append(module)

# Add connections
for filename in imports:
    for module in filename.imports:
        dot.edge(module, filename.name)


# print(dot.source)
dot.render('output.gv')
