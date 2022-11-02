# import packages
import pandas as pd

from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column, row
from bokeh.models import BoxAnnotation, BoxZoomTool, ColumnDataSource, CustomJS, DataTable, HoverTool, PanTool, TableColumn, TapTool

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
output_file("Boroughs_Nets.html")
p1 = figure(width=1500, height=500, tools="pan,wheel_zoom,reset")
nonsel_color = '#f8faa2'
sel_color = 'orange'
nosel_color = '#42b9f5'
high_color = 'green'

# bokeh ColumnDataSource1 = (x, y) placeholder coordinates for start and end points of each link
source1 = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# bokeh ColumnDataSource2 = DataFrame, itself
source2 = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': []})

# bokeh ColumnDataSource3 = associating Col2, Col1, and (x, y) coordinates
source3 = ColumnDataSource({"x":x,"y":y,'Col2':list(data['Col2']),
                            'Col1':list(data['Col1']), 'Col3':list(data['Col3']), 'Links':links_list,
                            'color':[nonsel_color]*len(x)})

# Set up line segment and circle frameworks
cr = p1.circle(x='x', y='y', color=nosel_color, size=6, alpha=1, 
              hover_color='orange', hover_alpha=1.0, source=source3,
              selection_color=high_color,
              nonselection_fill_color='color', nonselection_fill_alpha=1)
sr1 = p1.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.4, line_width=.5, source=source1)
sr2 = p1.segment(x0='x0', y0='y0', x1='x1', y1='y1', color='red', alpha=0.4, line_width=.5, source=source2)

# Add JS string for HoverTool Callback
hov_code = """
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

# JavaScript code for minimap
mmp_code = """
    box[%r] = cb_obj.start
    box[%r] = cb_obj.end
"""

# Create the box that functions as the current view in the minimap
box = BoxAnnotation(left=0, right=0, bottom=0, top=0, fill_alpha=0.1, line_color='black', fill_color='black')

# Establish Tooltips
TOOLTIPS = [("Col2","@Col2"), ("Col1","@Col1")]

# Create callbacks for HoverTool and TapTool
hov_cb = CustomJS(args={'circle': cr.data_source, 'segment': sr1.data_source}, code=hov_code)
tap_cb = CustomJS(args={'circle': cr.data_source, 'segment': sr2.data_source}, code=tap_code)
xcb = CustomJS(args=dict(box=box), code=mmp_code % ('left', 'right'))
ycb = CustomJS(args=dict(box=box), code=mmp_code % ('bottom', 'top'))

# Add HoverTool, PanTool-Horizontal, PanTool-Vertical, BoxZoomTool, and TapTool to main graph
p1.add_tools(HoverTool(tooltips=TOOLTIPS, callback=hov_cb, renderers=[cr]))
p1.add_tools(TapTool())
p1.add_tools(PanTool(dimensions='width'))
p1.add_tools(PanTool(dimensions='height'))
p1.add_tools(BoxZoomTool(match_aspect=True))

# Call the tap_cb CustomJS callback when you tap
source3.selected.js_on_change('indices', tap_cb)

# Create DataTable
columns = [TableColumn(field='Col2', title="Col2"), TableColumn(field='Col3', title="Col3"), TableColumn(field='Col1', title="Col1")]
data_table = DataTable(source=source3, columns=columns, width=400, height=280, scroll_to_selection=True, selectable=True)

# Dictate view window behavior
p1.x_range.js_on_change('start', xcb)
p1.x_range.js_on_change('end', xcb)
p1.y_range.js_on_change('start', ycb)
p1.y_range.js_on_change('end', ycb)

# Create minimap graph
p2 = figure(width=400, height=160)
cr2 = p2.circle(x='x', y='y', color=nosel_color, size=1, alpha=1, source=source3)
p2.axis.visible = False
p2.toolbar.logo = None
p2.toolbar_location = None
p2.xgrid.grid_line_color = None
p2.ygrid.grid_line_color = None
p2.add_layout(box)

# Order the graphs and the DataTable, then display them
layout = row(p1, column(p2, data_table))

show(layout)
