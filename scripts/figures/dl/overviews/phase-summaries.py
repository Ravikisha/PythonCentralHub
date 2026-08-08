"""One summary figure per phase, for the nine phase overview pages.

Every other figure in this module measures one thing on one page. These nine
measure the *phase*: each bar is a claim a page set out to test, and its colour
says whether the measurement confirmed the standard story or contradicted it.

The numbers are not re-measured here -- they are collected from the runs that
produced each page's own figures, on this machine, and every row names the page
it came from. That makes these aggregation figures rather than experiments, and
the captions say so. What they add is the view no single page can give: how
often the standard advice survived contact with a measurement.

``phase-1`` .. ``phase-9``
    Confirmed against refuted, one bar per page, annotated with the numbers.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _style import Palette, figure  # noqa: E402

# (page, the claim tested, verdict, effect, detail)
# verdict: "held" the standard story survived, "broke" it did not,
#          "cost"  it held but cost more than it was worth.
PHASES = {
    1: ("Neural Network Foundations", [
        ("Perceptron", "a single neuron can learn any gate", "broke",
         0.75, "XOR tops out at 3 of 4 rows, in all 40,401 weight pairs"),
        ("MLP", "more layers means more accuracy", "broke",
         0.0049, "8 layers scored 0.9047 against 2 layers' 0.9075"),
        ("Activations", "ReLU beats sigmoid", "held",
         0.30, "sigmoid loses 0.30 accuracy once the network is deep"),
        ("Autograd", "reverse mode is cheaper for many parameters", "held",
         174.4, "174x at 800 parameters, on identical machinery"),
        ("PyTorch", "the frameworks compute the same thing", "held",
         7.45e-09, "gradients agree to 7.45e-09 on gradients of size 0.0386"),
        ("Learning rate", "too large a rate explodes", "broke",
         0.0105, "lr=1.0 did not diverge; it matched lr=0.1 to 0.0105"),
    ]),
    2: ("Training Deep Neural Networks", [
        ("Optimizers", "Adam beats SGD", "held",
         0.0217, "0.9243 against 0.9026 at the same epoch budget"),
        ("Batch norm", "batch norm always helps", "broke",
         0.7833, "default momentum 0.99 reported 0.1540 on a short run"),
        ("Dropout", "dropout improves generalisation", "cost",
         0.0069, "helps only past the capacity where overfitting starts"),
        ("LR schedules", "a schedule beats a constant rate", "held",
         0.0121, "cosine 0.9364 against a tuned constant 0.9243"),
        ("Evaluation", "one held-out split is enough", "broke",
         0.0268, "the same model scored 0.0268 apart across splits"),
        ("Workflow", "scale up until you overfit", "cost",
         0.0150, "146x the parameters bought 0.0150 of validation accuracy"),
    ]),
    3: ("Computer Vision with CNNs", [
        ("Convolution", "weight sharing is cheaper than dense", "held",
         5376.0, "896 parameters against 4,816,928, independent of size"),
        ("Pooling", "strided convolution replaces pooling", "broke",
         0.0285, "strided came last: 0.8455 against average pooling 0.8740"),
        ("ResNet", "residual connections help at any depth", "broke",
         0.0067, "plain beat residual at 12 convolutions"),
        ("Transfer", "pretrained beats from scratch", "cost",
         0.0014, "fine-tuning won by 0.0014; a wrong rate cost 0.4026"),
        ("Augmentation", "augmentation improves accuracy", "broke",
         0.1855, "cost 0.1855 on canonical data, bought 0.1105 on rotated"),
        ("ViT", "transformers need enormous data", "broke",
         4000.0, "the ViT beat the convnet at 1,000 and 4,000 rows"),
    ]),
    4: ("Sequence Models with RNNs", [
        ("SimpleRNN", "recurrence beats order-free models", "broke",
         0.2148, "0.5856 against embedding-averaging's 0.8004"),
        ("Masking", "padding is handled for you", "broke",
         0.5036, "post-padding without a mask scored chance, silently"),
        ("LSTM", "gates fix long-range memory", "cost",
         0.32, "held to 100 steps at 0.0152, failed at 200"),
        ("Forecasting", "recurrence is needed for time series", "broke",
         0.0064, "a flat Dense layer lost by 0.0064 at a quarter the cost"),
        ("Refinements", "bidirectional layers help", "cost",
         0.0024, "+0.0188 fell to +0.0024 once width was matched"),
        ("Attention", "a fixed state can carry the input", "broke",
         0.9983, "0.0017 exact matches against attention's 1.0000"),
    ]),
    5: ("NLP & Transformers", [
        ("Bag of words", "neural models beat count features", "broke",
         0.0170, "TF-IDF 0.8632 against a transformer's 0.8462, 55x cheaper"),
        ("Subwords", "BPE removes out-of-vocabulary tokens", "held",
         0.0293, "OOV 0.0000 at 2,070 pieces against 0.0293 for words"),
        ("Embeddings", "embeddings capture meaning", "broke",
         1.0, "sentiment-trained vectors collapse to cosine 1.000"),
        ("NER", "token accuracy measures tagging", "broke",
         0.3622, "token 0.8011 against entity F1 0.4389"),
        ("Attention", "one attention block composes operations", "broke",
         0.6870, "one block 0.3120, two blocks 0.9990"),
        ("Transformer", "every component earns its place", "cost",
         0.0612, "at 1 block all ablations helped; layer norm pays at 4"),
    ]),
    6: ("Generative Deep Learning", [
        ("Autoencoders", "a learned encoder beats PCA", "cost",
         3.3, "true at 8 dims, false at 128 where PCA won by 3.3x"),
        ("VAE", "the KL term makes the latent samplable", "held",
         183.337, "KL 183.337 at beta=0; posterior collapse at beta=20"),
        ("GANs", "GANs trade coverage for sharpness", "broke",
         5.0, "the best run covered 5 of 10 classes and lost on confidence"),
        ("Evaluation", "FID measures generative quality", "broke",
         4.578, "copying 200 real images scored 5.027 against real 9.605"),
        ("Diffusion", "a broken noise schedule caused bad samples", "broke",
         1.4791, "fixing terminal SNR moved KL 12.9494 to 14.4285"),
        ("Text", "temperature trades coherence for variety", "held",
         0.42, "measured as word validity against n-gram diversity"),
    ]),
    7: ("Reinforcement Learning", [
        ("Exploration", "greedy is worse than epsilon-greedy", "cost",
         2394.4, "true on average, but greedy's seeds ranged 0.00 to 2394.40"),
        ("Discount", "gamma is a technical detail", "broke",
         0.0975, "it switches the optimal route; goal rate 0.7925 to 0.8900"),
        ("DQN", "replay and target networks each help", "broke",
         90.75, "only together: 144.20 against 53.45 for either alone"),
        ("Baselines", "variance reduction improves learning", "broke",
         0.27, "the gradient norm fell 35x and the score moved 0.27"),
        ("PPO", "clipping is what makes PPO stable", "cost",
         185.0, "worthless at 4 reuse steps; at 16 it saved a seed from 9.2"),
        ("Actor-critic", "a learned critic beats a batch mean", "broke",
         0.8, "195.0 against 194.2, for a second network and 7.3s"),
    ]),
    8: ("Scaling & Deploying Deep Models", [
        ("tf.data", "add num_parallel_calls for a big win", "broke",
         3.53, "tf.data had already applied 3.53x of the 3.93x"),
        ("Custom loops", "hand-written loops are slower", "cost",
         9.9, "matched fit to 0.0010; forgetting tf.function costs 9.9x"),
        ("Distribution", "distribution is nearly free", "broke",
         1.50, "one replica costs 1.50x before parallelising anything"),
        ("Mixed precision", "one line, roughly 2x faster", "broke",
         40.65, "40.65x SLOWER here - it is a GPU feature"),
        ("Serving", "serving is a packaging step", "broke",
         0.8575, "client-side preprocessing skew: 0.9470 to 0.0895"),
        ("Compression", "compression costs accuracy", "broke",
         0.0040, "pruning 50% improved it, 0.9773 against 0.9733"),
    ]),
    9: ("Capstone Projects", [
        ("Capstone 1", "a held-out score measures the model", "broke",
         0.4207, "augmentation lost 0.0130 clean, won 0.4207 three pixels on"),
        ("Capstone 1", "each rung of a ladder buys something", "cost",
         0.0130, "the last rung's gain was negative on the clean split"),
        ("Capstone 2", "sequence models beat bag of words on text", "broke",
         0.0550, "0.8507 in 3s against self-attention's 0.7957 in 165s"),
        ("Capstone 2", "the models make the same mistakes", "broke",
         0.0370, "an oracle picking per review would score 0.8957"),
        ("Capstone 3", "FID separates a generator from a copier", "broke",
         0.918, "the memoriser scored 16.425 against the VAE's 17.343"),
        ("Capstone 3", "a nearest-neighbour check catches copying", "broke",
         5.3904, "5.3939 against held-out data; 0.0035 against training"),
    ]),
}

COLOURS = {"held": "green", "broke": "red", "cost": "amber"}
VERDICT_LABEL = {
    "held": "the standard story held",
    "broke": "the measurement contradicted it",
    "cost": "it held, and cost more than it was worth",
}


@functools.lru_cache(maxsize=1)
def _tally() -> dict:
    out = {}
    for number, (_, rows) in PHASES.items():
        counts = {"held": 0, "broke": 0, "cost": 0}
        for row in rows:
            counts[row[2]] += 1
        out[number] = counts
    return out


def _draw_phase(number: int):
    def draw(fig, axes, p: Palette) -> None:
        title, rows = PHASES[number]
        ax = fig.subplots(1, 1)
        positions = np.arange(len(rows))
        palette = {"green": p.green, "red": p.red, "amber": p.amber}
        # Effects span many orders of magnitude (0.0014 to 5,376), so the bar
        # length is the log of the effect and the real number is printed.
        lengths = [np.log10(max(row[3], 1e-9)) + 9 for row in rows]
        colours = [palette[COLOURS[row[2]]] for row in rows]
        ax.barh(positions, lengths, color=colours, height=0.62)
        for position, row in zip(positions, rows):
            ax.annotate(row[4], (0.15, position), fontsize=7.2, color=p.bg,
                        va="center", ha="left")
        ax.set_yticks(positions)
        ax.set_yticklabels([f"{row[0]}\n{row[1]}" for row in rows],
                           fontsize=7.5)
        ax.set_xticks([])
        ax.set_xlim(0, max(lengths) * 1.02)
        counts = _tally()[number]
        ax.set_title(
            f"Phase {number} — {title}\n"
            f"{counts['broke']} of {len(rows)} claims contradicted, "
            f"{counts['cost']} held at a price, {counts['held']} held",
            fontsize=10)
        ax.invert_yaxis()

        handles = []
        for key in ("held", "cost", "broke"):
            handles.append(ax.barh([0], [0], color=palette[COLOURS[key]],
                                   label=VERDICT_LABEL[key]))
        ax.legend(fontsize=7, loc="lower right", framealpha=0.9)

    return draw


FIGURES = [figure(f"phase-{number}", _draw_phase(number), size=(9.0, 4.2),
                  axes=False)
           for number in sorted(PHASES)]


if __name__ == "__main__":
    tally = _tally()
    print("=== how the standard story fared, per phase ===")
    print(f"{'phase':>6} {'claims':>7} {'contradicted':>13} {'held at a cost':>15} "
          f"{'held':>6}")
    totals = {"held": 0, "broke": 0, "cost": 0}
    for number, (title, rows) in PHASES.items():
        counts = tally[number]
        for key in totals:
            totals[key] += counts[key]
        print(f"{number:6d} {len(rows):7d} {counts['broke']:13d} "
              f"{counts['cost']:15d} {counts['held']:6d}")
    total = sum(totals.values())
    print(f"\n{total} claims tested across 9 phases")
    print(f"  contradicted outright : {totals['broke']:3d} "
          f"({totals['broke'] / total:.1%})")
    print(f"  held, but at a price  : {totals['cost']:3d} "
          f"({totals['cost'] / total:.1%})")
    print(f"  held as advertised    : {totals['held']:3d} "
          f"({totals['held'] / total:.1%})")
