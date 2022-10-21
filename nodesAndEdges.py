# import packages
import pandas as pd

from bokeh.plotting import figure, output_file, show
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, CustomJS, DataTable, HoverTool, TableColumn, TapTool

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
    
# Bokeh setup
output_file("sanitized_data.html")
p = figure(width=1500, height=500)
nonsel_color = '#f8faa2'
sel_color = 'orange'
nosel_color = '#42b9f5'
    
# bokeh ColumnDataSource1 = (x, y) placeholder coordinates for start and end points of each link
source1 = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# bokeh ColumnDataSource2 = DataFrame, itself
source2 = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# bokeh ColumnDataSource3 = associating Col2, Col1, and (x, y) coordinates
source3 = ColumnDataSource({"x":x,"y":y,'Col2':list(data['Col2']),'Col1':list(data['Col1']), 'Col3':list(data['Col3']), 'Links':links_list, 'color':[nonsel_color]*len(x)})

# Set up line segment and circle frameworks
cr = p.circle(x='x', y='y', color=nosel_color, size=6, alpha=1, 
              hover_color='orange', hover_alpha=1.0, source=source3,
              selection_color=sel_color,
              nonselection_fill_color='color', nonselection_fill_alpha=1)
sr1 = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.7, line_width=.5, source=source1)
sr2 = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='orange', alpha=0.7, line_width=.5, source=source2)

# JavaScript code for HoverTool CustomJS callback: draw line between hovered-over glyph and all other glyphs on the same Net
hov_code = """
const links = %s;
const data = {'x0': [], 'y0': [], 'x1': [], 'y1': []};
const indices = cb_data.index.indices;
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

# JavaScript code for TapTool CustomJS callback: make lines remain if you click on a glyph
tap_code = """
const links = %s;
for (let j = 0; j < circle.data.color.length; j++) {
    circle.data.color[j]='%s';
}
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
        circle.data.color[end]='%s';
    }
}
circle.change.emit();
segment.data = data;
""" % (links, nonsel_color, sel_color)

# Establish Tooltips
TOOLTIPS = [("Col2","@Col2"), ("Col1","@Col1")]

# Create JavaScript Callbacks
hov_cb = CustomJS(args={'circle': cr.data_source, 'segment': sr1.data_source}, code=hov_code)
tap_cb = CustomJS(args={'circle': cr.data_source, 'segment': sr2.data_source}, code=tap_code)

# Add tools to the Graph
p.add_tools(HoverTool(tooltips=TOOLTIPS, callback=hov_cb, renderers=[cr]))
p.add_tools(TapTool())

# Call the tap_cb CustomJS callback when you tap
source3.selected.js_on_change('indices', tap_cb)

# Create DataTable
columns = [TableColumn(field='Col2', title="Col2"), TableColumn(field='Col1', title="Col1"), TableColumn(field='Col3', title="Col3")]
data_table = DataTable(source=source3, columns=columns, width=400, height=280, scroll_to_selection=True, selectable=True)

# Order the graph and display it
layout = row(p, data_table)
show(layout)
