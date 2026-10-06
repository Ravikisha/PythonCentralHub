/**
 * AlgorithmCard — the at-a-glance summary that closes every algorithm page in
 * the Machine Learning module.
 *
 * One consistent shape across ~40 pages means a reader can compare KNN against
 * SVM against Random Forest without re-reading the prose.
 *
 * Server component: it is a table of facts, with nothing to interact with.
 */
export interface Hyperparam {
  name: string;
  effect: string;
  /** Optional default value, rendered as a monospace chip. */
  default?: string;
}

export interface Complexity {
  /** Training cost, e.g. "O(n·d²)". */
  train?: string;
  /** Per-instance prediction cost. */
  predict?: string;
  /** Memory held by the fitted model. */
  memory?: string;
}

export interface AlgorithmCardProps {
  /** Algorithm name, e.g. "K-Means". */
  name: string;
  /** Short taxonomy line, e.g. "Unsupervised · Clustering". */
  type?: string;
  /** Fully qualified scikit-learn class (or other library entry point). */
  sklearn?: string;
  /** What the algorithm assumes about the data. */
  assumptions?: string[];
  complexity?: Complexity;
  /** The handful of hyperparameters that actually matter. */
  hyperparams?: Hyperparam[];
  useWhen?: string[];
  avoidWhen?: string[];
  /** Notation legend: n = samples, d = features, unless overridden. */
  notation?: string;
}

export function AlgorithmCard({
  name,
  type,
  sklearn,
  assumptions = [],
  complexity,
  hyperparams = [],
  useWhen = [],
  avoidWhen = [],
  notation = "n = samples, d = features, i = iterations",
}: AlgorithmCardProps) {
  const hasComplexity =
    !!complexity &&
    !!(complexity.train || complexity.predict || complexity.memory);

  return (
    <section className="pch-algo" aria-label={`${name} summary card`}>
      <div className="pch-viz__bar">
        <span className="pch-viz__tag">algorithm</span>
        <span className="pch-viz__title">{name}</span>
        {type ? <span className="pch-algo__type">{type}</span> : null}
      </div>

      <div className="pch-algo__body">
        {sklearn ? (
          <p className="pch-algo__api">
            <span className="pch-algo__api-label">API</span>
            <code>{sklearn}</code>
          </p>
        ) : null}

        {assumptions.length > 0 ? (
          <div className="pch-algo__block">
            <h4 className="pch-algo__h">Assumes</h4>
            <ul>
              {assumptions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {hasComplexity ? (
          <div className="pch-algo__block">
            <h4 className="pch-algo__h">Cost</h4>
            <dl className="pch-algo__cost">
              {complexity?.train ? (
                <div>
                  <dt>train</dt>
                  <dd>
                    <code>{complexity.train}</code>
                  </dd>
                </div>
              ) : null}
              {complexity?.predict ? (
                <div>
                  <dt>predict</dt>
                  <dd>
                    <code>{complexity.predict}</code>
                  </dd>
                </div>
              ) : null}
              {complexity?.memory ? (
                <div>
                  <dt>memory</dt>
                  <dd>
                    <code>{complexity.memory}</code>
                  </dd>
                </div>
              ) : null}
            </dl>
            <p className="pch-algo__notation">{notation}</p>
          </div>
        ) : null}

        {hyperparams.length > 0 ? (
          <div className="pch-algo__block">
            <h4 className="pch-algo__h">Hyperparameters that matter</h4>
            <ul className="pch-algo__params">
              {hyperparams.map((h, i) => (
                <li key={i}>
                  <code className="pch-algo__param-name">{h.name}</code>
                  {h.default ? (
                    <span className="pch-algo__default">
                      default {h.default}
                    </span>
                  ) : null}
                  <span className="pch-algo__param-effect">{h.effect}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {useWhen.length > 0 || avoidWhen.length > 0 ? (
          <div className="pch-algo__verdict">
            {useWhen.length > 0 ? (
              <div className="pch-algo__col pch-algo__col--yes">
                <h4 className="pch-algo__h">Reach for it when</h4>
                <ul>
                  {useWhen.map((u, i) => (
                    <li key={i}>{u}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {avoidWhen.length > 0 ? (
              <div className="pch-algo__col pch-algo__col--no">
                <h4 className="pch-algo__h">Look elsewhere when</h4>
                <ul>
                  {avoidWhen.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </section>
  );
}

export default AlgorithmCard;
