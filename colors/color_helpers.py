def rgb_from_hex( hex_ ) :
    r = int( hex_[0:2], 16 )
    g = int( hex_[2:4], 16 )
    b = int( hex_[4:6], 16 )
    return r,g,b

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v

def rgb_to_hsl(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, l = ((high + low) / 2,)*3

    if high == low:
        h = 0.0
        s = 0.0
    else:
        d = high - low
        s = d / (2 - high - low) if l > 0.5 else d / (high + low)
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, l

FLOAT_ERROR = 1e-8

def hsl_to_rgb( h, s, l ) :

    if not (0.0 - FLOAT_ERROR <= s <= 1.0 + FLOAT_ERROR):
        raise ValueError("Saturation must be between 0 and 1.")
    if not (0.0 - FLOAT_ERROR <= l <= 1.0 + FLOAT_ERROR):
        raise ValueError("Lightness must be between 0 and 1.")

    if s == 0:
        return l, l, l

    if l < 0.5:
        v2 = l * (1.0 + s)
    else:
        v2 = (l + s) - (s * l)

    v1 = 2.0 * l - v2

    r = _hue2rgb(v1, v2, h + (1.0 / 3))
    g = _hue2rgb(v1, v2, h)
    b = _hue2rgb(v1, v2, h - (1.0 / 3))

    return r,g,b

def _hue2rgb(v1, v2, vH):
    """Private helper function (Do not call directly)
    :param vH: rotation around the chromatic circle (between 0..1)
    """
    while vH < 0: vH += 1
    while vH > 1: vH -= 1

    if 6 * vH < 1: return v1 + (v2 - v1) * 6 * vH
    if 2 * vH < 1: return v2
    if 3 * vH < 2: return v1 + (v2 - v1) * ((2.0 / 3) - vH) * 6

    return v1


JS_HELPERS = """
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

def read_colors() :
    import csv

    filename =  'rgb.txt'
    colors = []
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            if row[0] == '#':
                continue
            try:
                name = row[0]

                # Reserve "black" and "white" for true black and white
                if name == "black" or name == "white":
                    continue

                #srgb = sRGBColor.new_from_rgb_hex(row[1])
                r,g,b = rgb_from_hex( row[1][1:] )
                h,s,l = rgb_to_hsl( r/255.0,g/255.0,b /255.0 )
                colors.append({
                    "name": name,
                    "hex": row[1],
                    "r" : r, "g" : g, "b" : b,
                    "h" : h * 100, "s" : s * 100, "l" : l * 100,
                })
            except Exception as exc:
                print( row, "\n", exc )


    return colors

def get_colors_dict( colors ) :
    colors_dict = { "name" : [], "hex" : [], "r" : [], "g" : [], "b" : [], "h" : [], "s" : [], "l" : [] }
    for color in colors :
        for k  in colors_dict.keys() :
            colors_dict[k].append( color[k] )

    return colors_dict



