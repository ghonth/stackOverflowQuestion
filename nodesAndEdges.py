# import packages
import pandas as pd

from bokeh.models import ColumnDataSource, CustomJS, HoverTool, TapTool
from bokeh.plotting import figure, output_file, show

# Read in the DataFrame
data = pd.read_csv("sanitized_data.csv")

# Generate (x, y) data from DataFrame
x = list(data["X"])
y = list(data["Y"])

# Generate dictionary of links; for each Col1, I want 
    # there to be a link between each Col3 and every other Col3 in the same Col1
links = {data["Col2"].index[index]:list(data[(data["Col1"]==data["Col1"][index]) & (data["Col2"]!=data["Col2"][index])].index) for index in data["Col2"].index}
links_list = []
for key in links.keys():
    links_list.append(links[key])
    
# bokeh ColumnDataSource1 = (x, y) placeholder coordinates for start and end points of each link
source1 = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# bokeh ColumnDataSource2 = DataFrame, itself
source2 = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# bokeh ColumnDataSource3 = associating Col2, Col1, and (x, y) coordinates
source3 = ColumnDataSource({"x":x,"y":y,'Col2':list(data['Col2']),'Col1':list(data['Col1']), 'Links':links_list})

# Set up Graph and Output file
output_file("sanitized_example.html")
p = figure(width=1900, height=700)

# Set up line segment and circle frameworks
sr1 = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.4, line_width=.5, source=source1)
sr2 = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.4, line_width=.5, source=source2)
cr = p.circle(x='x', y='y', color='blue', size=5, alpha=1, hover_color='orange', hover_alpha=1.0, source=source3)

# Add JS string for HoverTool Callback
code_for_hover = """
const links = %s
const data = {'x0': [], 'y0': [], 'x1': [], 'y1': []}
const indices = cb_data.index.indices
for (let i = 0; i < indices.length; i++) {
    const start = indices[i]
    for (let j = 0; j < links[start].length; j++) {
        const end = links[start][j]
        data['x0'].push(circle.data.x[start])
        data['y0'].push(circle.data.y[start])
        data['x1'].push(circle.data.x[end])
        data['y1'].push(circle.data.y[end])
    }
}
segment.data = data
""" % links

# Add JS string for Tap segments
code_for_tap = """
const links = %s;
const data = {'x0': [], 'y0': [], 'x1': [], 'y1': []};
const indices = cb_obj.indices;
for (let i = 0; i < indices.length; i++) {
    const start = indices[i];
    for (let j = 0; j < links[start].length; j++) {
        const end = links[start][j];
        data['x0'].push(circle.data.x[start]);
        data['y0'].push(circle.data.y[start]);
        data['x1'].push(circle.data.x[end]);
        data['y1'].push(circle.data.y[end]);
    }
}
segment.data = data;
""" % links

# Establish Tooltips
TOOLTIPS = [("Col2","@Col2"), ("Col1","@Col1")]

# Create JavaScript Callbacks
callback_on_hover = CustomJS(args={'circle': cr.data_source, 'segment': sr1.data_source}, code=code_for_hover)
callback_on_tap = CustomJS(args={'circle': cr.data_source, 'segment': sr2.data_source}, code=code_for_tap)

# Add tools to the Graph
p.add_tools(HoverTool(tooltips=TOOLTIPS, callback=callback_on_hover, renderers=[cr]))
p.add_tools(TapTool())
source3.selected.js_on_change('indices', callback_on_tap)

# Show the graph
show(p)
