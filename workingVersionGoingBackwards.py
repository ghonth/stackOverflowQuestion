from bokeh.models import ColumnDataSource, CustomJS, Div, HoverTool, Row,TapTool
from bokeh.plotting import figure, output_file, show


output_file("toolbar.html")

source5 = ColumnDataSource(data = dict(
xo = [1, 2, 3, 3, 4],
yo = [2, 5, 8, 3, 6],
desc = ['A', 'B', 'C', 'D', 'E'],
imgs = ['https://docs.bokeh.org/static/snake.jpg',
        'https://docs.bokeh.org/static/snake2.png',
        'https://dods.bokeh.org/static/snake3D.png',
        'https://docs.bokeh.org/static/snake4_TheRevenge.png',
        'https://docs.bokeh.org/static/snakebite.jpg'],
fonts = ['<i>italics</i>',
         '<pre>pre</pre>',
         '<b>bold</b>',
         '<small>small</small>',
         '<del>del</del>' ]))

TOOLTIPS2 = """
<div>
    <div>
        <img
            src="@imgs" height="84" alt="@imgs" width="84"
            style="float: left; margin: 0px 15px 15px 0px;"
            border="2"/>
    </div>
    <div width=60px>
        <span style="font-size: 17px; font-weight: bold;">@desc</span>
        <span style="font-size: 15px; color: #966;">[$index]</span>
    </div>
    <div>
        <span>@fonts{safe}</span>
    </div>
    <div>
        <span style="font-size: 15px;">Location</span>
        <span style="font-size: 10px; color: #696;">($x, $y)</span>
    </div>
</div> """

p2 = figure(plot_width = 400, plot_height = 400, x_range = (0, 6), y_range = (1, 9),
      title = "Mouse over the dots", tools = 'pan,wheel_zoom,save,reset,tap')
circles = p2.circle('xo', 'yo', size = 20, source = source5)
div = Div(text = '<div id="tooltip" style="position: absolute; display: none"></div>', name = 'tooltip')

code2 = '''  if (cb_data.source.selected.indices.length > 0){
                var selected_index = cb_data.source.selected.indices[0];
                var tooltip = document.getElementById("tooltip");

                tooltip.style.display = 'block';
                tooltip.style.left = Number(cb_data.geometries.sx) + Number(20) + 'px';
                tooltip.style.top = Number(cb_data.geometries.sy) - Number(20) + 'px';

                tp = tp.replace('@imgs', cb_data.source.data.imgs[selected_index]);
                tp = tp.replace('@desc', cb_data.source.data.desc[selected_index]);
                tp = tp.replace('@fonts{safe}', cb_data.source.data.fonts[selected_index]);
                tp = tp.replace('$index', selected_index);
                tp = tp.replace('$x', Math.round(cb_data.geometries.x));
                tp = tp.replace('$y', Math.round(cb_data.geometries.y));
                tooltip.innerHTML = tp;
          } '''
p2.select(TapTool).callback = CustomJS(args = {'circle': circles, 'plot': p2, 'tp': TOOLTIPS2}, code = code2)
#p2.select(TapTool).callback = CustomJS(args = {'circles': circles, 'plot': p2}, code = code2)
p2.add_tools(HoverTool(tooltips=TOOLTIPS2))

source5.selected.js_on_change('indices', CustomJS(code = 'if (cb_obj.indices.length == 0) document.getElementById("tooltip").style.display = \"none\"'))
layout = Row(p2, div)
show(layout)
