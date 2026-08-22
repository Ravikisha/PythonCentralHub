# Mathematics for Machine Learning — step-through labs

Interactive, scrubbable visualizations for the *Mathematics for Machine Learning*
module. 12 labs so far, all on the same chassis as the DSA visualizations one
directory up: `AutodiffGraph`, `DescentLab`, `DistributionLab`, `EigenLab`, `ElimStepper`, `MatrixLab`, `NormBall`, `ProjectionLab`, `SVDLab`, `SpanExplorer`, `SurfaceGrad`, `TaylorLab`.
The tag table below also names the labs still to be built, so the planned shape of
the module is visible from here.

## Why these exist alongside the p5 sketches

The module has two kinds of visual and they are not interchangeable.

A **p5 sketch** is an animation with in-canvas knobs. It is the right tool when
the reader should *feel* a continuous relationship: drag `p` and watch the unit
ball morph, drag the vector and watch its shadow slide along the line. Nothing
is stepping; there is no "step 4" to stop on.

A **lab** is a step-through of an *iterative* argument. Gaussian elimination has
a third pivot. EM has a seventh iteration. Reverse-mode autodiff has a node
where the adjoint accumulates from two parents. Those are the moments a reader
gets stuck, and an animation that keeps going is exactly the wrong medium for
them. `VizPlayer` gives step ±1, scrub, speed, keyboard control and a per-frame
caption, so the reader stops on the frame they do not understand and reads what
happened.

Rule of thumb: **if you can name the steps, it is a lab; if you can only name
the parameters, it is a p5 sketch.**

## Architecture

Identical to `src/components/viz/README.md`, and deliberately so:

```
algorithm (pure)  ──▶  Frame[]  ──▶  VizPlayer (transport)  ──▶  stage renderer
 algos/*.ts            frames.ts     ../VizPlayer.tsx           this directory
```

An **algorithm** in `algos/` walks its own logic and pushes one `Frame` per
meaningful step. It never touches the DOM, never sets a timer, imports nothing
but `frames.ts`, and is therefore trivially testable in isolation.

**`VizPlayer`** owns all transport, plus the caption bar, the watch panel, the
code line-highlight, the result bar, reduced-motion handling and the pause-on-
hidden-tab behaviour. Labs never re-implement any of it.

A **stage renderer** is a pure function of one frame. Give it `frame.state` and
it returns SVG or HTML. It reads no React state of its own.

## Using one in MDX

```mdx
import ElimStepper from "../../../../components/viz/math/ElimStepper.tsx";

<ElimStepper
  client:visible
  matrix={[[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]}
  rhs={[8, -11, -3]}
  reduced
  title="Three pivots turn the system into an answer"
  desc="Watch the pivot ring move down the diagonal. Every row operation below it is chosen to zero one entry."
/>
```

`client:visible` is **required**. Without it the island renders frame 0 and never
hydrates, so the reader gets a static picture with dead buttons.

Every lab accepts `title` (required), `desc`, `lib`, `ms` and `autoPlay` on top
of its own data props.

## Tag pills

`VizPlayer` requires a `tag`, and the tag string is printed in the pill, so each
lab passes one that names what the reader is looking at. Six were added to the
`VizTag` union for this module; their colours and glyphs live in
`src/styles/math-viz.css`.

| tag | labs |
| --- | --- |
| `matrix` | `MatrixLab`, `ElimStepper`, `EigenLab`, `SVDLab` |
| `vector` | `SpanExplorer`, `NormBall`, `ProjectionLab` |
| `field` | `SurfaceGrad`, `TaylorLab`, `AutodiffGraph` |
| `dist` | `DistributionLab`, `BayesLab` |
| `opt` | `DescentLab`, `ConstraintLab`, `ConvexLab` |
| `fit` | `RegressionLab`, `PCALab`, `EMLab`, `MarginLab` |

## The labs

| component | what it steps through | chapters |
| --- | --- | --- |
| `MatrixLab` | a 2×2 or 3×3 map applied to a grid, one basis vector at a time; determinant as signed area | §2.2, §2.7, §4.1 |
| `ElimStepper` | Gaussian elimination → row echelon → reduced row echelon, pivot by pivot | §2.3 |
| `SpanExplorer` | adding vectors one at a time, testing each against the current span, extracting a basis | §2.4–2.6 |
| `NormBall` | unit balls at a sequence of `p` values | §3.1 |
| `ProjectionLab` | projection onto a line or plane; Gram–Schmidt one vector at a time | §3.5–3.8 |
| `EigenLab` | power iteration converging on the dominant eigenvector | §4.2, §4.4 |
| `SVDLab` | rank-k reconstruction, one singular value added per frame | §4.5–4.6 |
| `SurfaceGrad` | gradient field, directional derivatives, a walk along a contour | §5.2–5.3 |
| `TaylorLab` | Taylor polynomials of rising order around a fixed point | §5.8 |
| `AutodiffGraph` | forward pass node by node, then the reverse pass accumulating adjoints | §5.6 |
| `DistributionLab` | pdf/cdf sweeps, Gaussian conditioning and marginalisation | §6.2, §6.5 |
| `BayesLab` | prior → posterior, one observation per frame | §6.3, §6.6 |
| `DescentLab` | GD / momentum / SGD / Newton, one update per frame | §7.1–7.2 |
| `ConstraintLab` | the constrained optimum found by walking level sets to tangency | §7.2 |
| `ConvexLab` | chord test, epigraph, Jensen | §7.3 |
| `RegressionLab` | OLS, the ridge path as λ rises, the Bayesian predictive band | Ch 9 |
| `PCALab` | variance maximised direction by direction; reconstruction as components are added | Ch 10 |
| `EMLab` | E-step responsibilities, then M-step updates, with the log-likelihood climbing | Ch 11 |
| `MarginLab` | margin construction, support-vector identification, kernel substitution | Ch 12 |

## Writing a new one

1. **Write the algos module first.** `algos/<topic>.ts` exports its `*Input` and
   `*State` types and a pure function returning `Trace<*State>`, built with
   `tracer<*State>(CODE)` from `../../frames`. Wrap the return in `capFrames` if
   the step count depends on input size.
2. **Every frame gets a caption.** One present-tense sentence saying what *this*
   step did. `frames.ts` calls this the single most important field and it is
   right: the caption is what makes the thing a lesson rather than a loop.
3. **Put the numbers in `watch`.** Residual, log-likelihood, λ, current pivot —
   whatever the reader would otherwise have to infer from pixels.
4. **Use `phase` for two-part loops.** E-step/M-step, forward/backward,
   expand/shrink. It renders as a pill so the reader can see which half they are
   in.
5. **Then write the component.** A `useMemo` over the algos call, a pure
   `renderStage`, and a `<VizPlayer>`. If the component has `useState`, something
   has gone wrong — that state belongs in the trace.
6. **Numbers rendered in a stage are rounded for display only.** Never round in
   the algorithm; a reader who scrubs back should see the same values.

## What these labs do not do

- **No KaTeX inside a stage.** The islands render before the KaTeX pass and are
  hydrated client-side, so `$…$` in a stage is literal text. Stages use plain
  monospace notation (`A^T`, `lambda_1`, `x_2`); the real typeset mathematics is
  in the page prose around the lab.
- **No data fetching, no timers, no `Math.random()` outside a seeded helper.** A
  trace must be identical on the server and after hydration or React will
  complain, and a reader who reloads must see the same run.
