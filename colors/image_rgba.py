# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:50:50 2019

@author: mrestrepo
"""

from __future__ import division

import numpy as np

from bokeh.layouts import row, column, widgetbox
from bokeh.plotting import figure, show, output_file
from bokeh.models import CustomJS, Slider, ColumnDataSource
#%%
helpers = """
let hue2rgb = function hue2rgb(p, q, t){
            if(t < 0) t += 1;
            if(t > 1) t -= 1;
            if(t < 1/6) return p + (q - p) * 6 * t;
            if(t < 1/2) return q;
            if(t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
 };

let hslToRgb = function hslToRgb(h, s, l){
    var r, g, b;

    if(s == 0){
        r = g = b = l; // achromatic
    }else{
        
        var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        var p = 2 * l - q;
        r = hue2rgb(p, q, h + 1/3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1/3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
};
"""
#%%
N = 50
img = np.empty((N,N), dtype=np.uint32)
view = img.view(dtype=np.uint8).reshape((N, N, 4))
for i in range(N):
    for j in range(N):
        view[i, j, 0] = int(i/N*255)
        view[i, j, 1] = 158
        view[i, j, 2] = int(j/N*255)
        view[i, j, 3] = 255

p = figure(x_range=(0,100), y_range=(0,100))

source = ColumnDataSource( data=dict(x=[0], y=[0], image=[img]))

# must give a vector of images
#rgba = p.image_rgba(image=[img], x=0, y=0, dw=100, dh=100 )
rgba = p.image_rgba(image="image", x=0, y=0, dw=100, 
                    dh=100, source=source)


callback = CustomJS(args=dict(source=source), code="""
    N = _N_ ;
    
    _helpers_; 
    
    let hue = cb_obj.value / 100.0;
    console.log("hue1", hue);
       
    a_pos = 256 * 256 * 256;
    b_pos = 256 * 256;
    g_pos = 256;
    r_pos = 1; 
    
    console.log("source.data", source.data);
    console.log("source[image]", source["image"]);
        
    let data = source.data["image"][0];
    for( i=0; i < N; i++ ) {
        for( j=0; j < N; j++ ) {
                //r = Math.trunc( i * (1.0 / N) * 255 ); 
                //g = Math.trunc( j * (1.0 / N) * 255 ); 
                //b = 128;
                let s = i * (1.0 / N);
                let l = j * (1.0 / N);
                let rgb = hslToRgb( hue, s, l ); 
                a = 255; 
                //data[ i * N + j ] = r * r_pos + g * g_pos + b * b_pos + a * a_pos;
                data[ i * N + j ] = rgb[0] * r_pos + rgb[1] * g_pos + rgb[2] * b_pos + a * a_pos;
        }
    }
    console.log("hue2", hue);
    
    source.change.emit();
""".replace( "_N_", str(N) ).replace("_helpers_", helpers )  ) ; # .replace( "_N_", str(N) )

hue_slider = Slider(start=00, end=100, value=50, step=1,
                    title="Hue", callback=callback)
# callback.args["hue"] = hue_slider

layout = column( p,  widgetbox(hue_slider) )

output_file("image_rgba.html", title="image_rgba.py example")

show(layout, browser=None)  # open a browser
#%%