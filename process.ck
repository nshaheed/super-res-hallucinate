// play it back at a given speed

string filename;
float rate;
if( me.args() ) {
    me.arg(0) => filename;
    me.arg(1) => Std.atof => rate;
}

// the patch 
SndBuf buf(filename, rate) => dac;


(1/rate)::buf.length() => now;

