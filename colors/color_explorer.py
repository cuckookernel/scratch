import numpy as np

from bokeh.plotting import figure
from bokeh.layouts import row, column, widgetbox
from bokeh.models import CustomJS, Slider, Dropdown, AutocompleteInput, ColumnDataSource, HoverTool

from color_helpers import hsl_to_rgb, JS_HELPERS

def create_init_img( N ) :
    img = np.empty((N,N), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((N, N, 4))
    init_hue = 0.5
    for i in range(N):
        for j in range(N):
            s = i * (1.0 / N)
            l = j * (1.0 / N)

            r, g, b = hsl_to_rgb( init_hue, s, l )
            view[i, j, 0] = int(255 * r)
            view[i, j, 1] = int(255 * g)
            view[i, j, 2] = int(255 * b)
            view[i, j, 3] = 255

    return img
            
def make_layout( N, colors_dict,  colors_arr, widget_size=300) :
    img = create_init_img( N )

    p = figure(x_range=(0,102), y_range=(0,102), 
               plot_width=widget_size, plot_height=widget_size, 
               tools="reset,wheel_zoom,box_zoom")

    source     = ColumnDataSource( data=dict(x=[0], y=[0], image=[img]))
    all_colors = ColumnDataSource( data=colors_dict )
    c_source   = ColumnDataSource( data={ "name": [], "hex" : [], "h" : [], "s" : [], "l" : [] }  )

    # must give a vector of images
    #rgba = p.image_rgba(image=[img], x=0, y=0, dw=100, dh=100 )
    p.image_rgba(image="image", x=0, y=0, dw=100, 
                        dh=100, source=source)

    p.circle( source=c_source, x="l", y="s", 
              fill_color=None, radius=3,
              line_color="white", line_width=1 )

    p.add_tools(HoverTool( tooltips=[
                                ( 'name',  '@name' ),
                                ( 'hex',  '@hex' ),
                                ( 'H',  '@h{%d}' ),
                                ( 'S',  '@s{%d}' ),
                                ( 'L',  '@l{%d}' )# use @{ } for field names with spaces
                                #( 'volume', '@volume{0.00 a}'      ),
                           ],            
                           formatters={ "hex" : "printf",
                                        "h"   : "printf",
                                        "s"   : "printf",
                                        "l"   : "printf"} ) )

    p.text( source=c_source, x="l", y="s", 
            text="name", text_font_size="8pt" )
    
    hue_callback = CustomJS(args=dict(source=source, 
                                  c_source=c_source, 
                                  all_colors=all_colors), 
                            code= read_file( "slider_callback.js" )
                                    .replace( "__N__", str(N) )
                                    .replace( "__helpers__", JS_HELPERS )  
                                    .replace( "__init_c_source__", 
                                            str( c_source.data ) ) ) 

    hue_slider = Slider(start=0, end=100, value=50, step=1,
                        title="Hue", callback=hue_callback)

    hue_slider.js_on_change('value', hue_callback)

    auto_complete=AutocompleteInput( completions = [ f"{c['name']:20s} HSL({int(c['h'])}%,{int(c['s'])}%,{int(c['l'])}%) "
                                                     f"RGB({int(c['r'])},{int(c['g'])},{int(c['b'])}) {c['hex']}" 
                                                     for c in colors_arr ] )

    dd_callback =  CustomJS(args=dict( hue_slider=hue_slider), 
                              code="""
                                console.log( cb_obj.value ); 
                                hue_slider.value = cb_obj.value;
                                hue_slider.change.emit();
                              """  )

    #color_name_dd = Dropdown( default_value="a", menu=dd_menu_tups, callback=dd_callback )

    # callback.args["hue"] = hue_slider

    layout = column( p,   widgetbox(hue_slider), widgetbox(auto_complete) )
    return layout 


def read_file( path ) : 
    with open( path, encoding="utf8" ) as f_in: 
        return f_in.read() 