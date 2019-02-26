    N = __N__ ;
    
    __helpers__; 
    
    let hue_pct = cb_obj.value; // this is in [0,100]
    let hue = cb_obj.value / 100.0; //  in [0.0, 1.0]
    
    // constants for creating 32 bit ints 
    let a_pos = 256 * 256 * 256;
    let b_pos = 256 * 256;
    let g_pos = 256;
    let r_pos = 1; 
    
    console.log("source.data", source.data);
    console.log("source[image]", source["   image"]);
    
    c_source.data = __init_c_source__;
    
    console.log( "before all_colors loop", Object.keys( c_source.data ) );
    for( cidx = 0; cidx < all_colors.data["name"].length; cidx++ ) {
        let color_h = all_colors.data["h"][cidx];
        
        if( Math.abs(color_h - hue_pct) < 2.0 ) {
            for( const k of Object.keys( c_source.data ) ) {
                // console.log( k, c_source.data[k]);
                c_source.data[k].push( all_colors.data[k][cidx] ); 
            }    
        }
    }
    // console.log( "after all_colors loop", c_source.data["name"].length );
    c_source.change.emit();
    
    let data = source.data["image"][0];
    for( i=0; i < N; i++ ) {
        for( j=0; j < N; j++ ) {
            //r = Math.trunc( i * (1.0 / N) * 255 ); 
            //g = Math.trunc( j * (1.0 / N) * 255 ); 
            //b = 128;
            a = 255; // alpha 

            let s = i * (1.0 / N);
            let l = j * (1.0 / N);
            let rgb = hslToRgb( hue, s, l );                 
            //data[ i * N + j ] = r * r_pos + g * g_pos + b * b_pos + a * a_pos;
            data[ i * N + j ] = rgb[0] * r_pos + rgb[1] * g_pos + rgb[2] * b_pos + a * a_pos;
        }
    }
    
    source.change.emit();