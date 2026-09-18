// SVGO configuration for the matplotlib-generated figures under public/images.
//
// Those files are ~99.5% path coordinate data, written by matplotlib with six
// decimal places on a viewBox only a few hundred units wide — far below one
// screen pixel. Rounding the PATH data is therefore free; rounding the
// DRAWING SURFACE is not, because it shifts the intrinsic height by a pixel,
// and the light and dark SVGs of one figure must stay the same size.
//
// So the two are configured separately:
//   convertPathData    -> floatPrecision 3   (where the bytes are)
//   cleanupNumericValues -> off              (leave width/height/viewBox alone)
//
// Precision 3 rather than 2: on a dense scatter with overlapping alpha
// markers, 2 gave a worst channel difference of 62/255 against 26/255 for 3,
// for 1.2 percentage points more compression. Not worth it.
export default {
  multipass: true,
  js2svg: { indent: 0, pretty: false },
  plugins: [
    {
      name: "preset-default",
      params: {
        overrides: {
          // Leave the root width/height alone. This plugin rewrites
          // matplotlib's "576.909858pt" to the exactly equivalent "769.213144"
          // — but dropping the unit changes how rasterisers resolve the
          // sub-pixel origin, which shifts EVERY anti-aliased edge in the
          // drawing. Measured: with this on, the worst channel difference is
          // 110/255 and 10.9% of pixels move; with it off, 19/255 and 1.5%,
          // for exactly the same output size.
          cleanupNumericValues: false,
          // this is the one that matters: path coordinate data
          convertPathData: { floatPrecision: 3, transformPrecision: 4 },
          // glyph <use> elements reference these ids; the saving from
          // renaming them is negligible next to the path data
          cleanupIds: false,
          // the Figure component scales by width, so the viewBox must stay
          removeViewBox: false,
        },
      },
    },
  ],
};
