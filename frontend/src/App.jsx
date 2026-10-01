import { useState } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const API_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  'http://127.0.0.1:8000'
).replace(/\/$/, '');
const starterAssets = [
  { name: 'Index fund', cost: 420, expected_return: 82 },
  { name: 'Treasury bonds', cost: 240, expected_return: 38 },
  { name: 'Growth equity', cost: 360, expected_return: 76 },
  { name: 'Dividend fund', cost: 290, expected_return: 53 },
];

function formatMs(value) {
  if (value === 0) return '0.000 ms';
  if (value < 0.001) return `${(value * 1000).toFixed(2)} µs`;
  return `${value.toFixed(3)} ms`;
}

export default function App() {
  const [assets, setAssets] = useState(starterAssets);
  const [budget, setBudget] = useState(800);
  const [algorithm, setAlgorithm] = useState('dp');
  const [draft, setDraft] = useState({ name: '', cost: '', expected_return: '' });
  const [result, setResult] = useState(null);
  const [benchmark, setBenchmark] = useState([]);
  const [maxAssets, setMaxAssets] = useState(19);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');

  async function post(path, body) {
    const response = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || 'The request could not be completed.');
    return payload;
  }

  async function runOptimization(event) {
    event.preventDefault();
    if (algorithm === 'brute_force' && assets.length > 23) {
      setError('Brute force is limited to 23 assets.');
      return;
    }
    setBusy('optimize');
    setError('');
    try {
      setResult(await post('/api/optimize', { assets, budget: Number(budget), algorithm }));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy('');
    }
  }

  async function runBenchmark() {
    setBusy('benchmark');
    setError('');
    try {
      const data = await post('/api/benchmark', {
        max_assets: Number(maxAssets),
        budget: Number(budget),
      });
      setBenchmark(data.points);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy('');
    }
  }

  function addAsset(event) {
    event.preventDefault();
    if (assets.length >= 25) {
      setError('A portfolio can contain at most 25 assets.');
      return;
    }
    if (!draft.name.trim() || !draft.cost || !draft.expected_return) return;
    setAssets([...assets, {
      name: draft.name.trim(),
      cost: Number(draft.cost),
      expected_return: Number(draft.expected_return),
    }]);
    setDraft({ name: '', cost: '', expected_return: '' });
    setResult(null);
  }

  function removeAsset(index) {
    setAssets(assets.filter((_, itemIndex) => itemIndex !== index));
    setResult(null);
  }

  return (
    <div className="app-shell">
      <aside className="rail">
        <a className="brand" href="#top" aria-label="Portfolio Lab home"><span className="brand-mark">P</span><span>PORTFOLIO<br />LAB</span></a>
        <div className="rail-rule" />
        <span className="rail-caption">DAA / 01</span>
        <div className="rail-bottom"><span className="live-dot" /> ALGORITHM STUDY</div>
      </aside>

      <main id="top" className="workspace">
        <header className="topbar">
          <div><span className="eyebrow">DESIGN &amp; ANALYSIS OF ALGORITHMS</span><h1>Portfolio optimizer</h1></div>
          <div className="course-tag"><span>0/1</span> KNAPSACK <span className="tag-divider">/</span> PERSONAL FINANCE</div>
        </header>

        <section className="intro-row">
          <div><p className="intro-copy">Select a portfolio under budget. Then compare the cost of finding it.</p></div>
          <div className="budget-control"><label htmlFor="budget">INVESTMENT BUDGET</label><div className="budget-input"><span>$</span><input id="budget" type="number" min="0" value={budget} onChange={(event) => setBudget(event.target.value)} /></div></div>
        </section>

        <section className="work-grid">
          <div className="panel asset-panel">
            <div className="panel-heading"><div><span className="section-index">01</span><h2>Candidate assets</h2></div><span className="count-pill">{assets.length} ASSETS</span></div>
            <div className="asset-table-wrap">
              <table className="asset-table">
                <thead><tr><th>ASSET</th><th>COST</th><th>RETURN</th><th><span className="sr-only">Remove</span></th></tr></thead>
                <tbody>
                  {assets.map((asset, index) => (
                    <tr key={`${asset.name}-${index}`}>
                      <td><span className={`asset-dot dot-${index % 4}`} />{asset.name}</td>
                      <td>${Number(asset.cost).toLocaleString()}</td>
                      <td className="return-cell">+${Number(asset.expected_return).toLocaleString()}</td>
                      <td><button className="icon-button" type="button" aria-label={`Remove ${asset.name}`} title="Remove asset" onClick={() => removeAsset(index)}>×</button></td>
                    </tr>
                  ))}
                  {assets.length === 0 && <tr><td className="empty-row" colSpan="4">Add an asset to start optimizing.</td></tr>}
                </tbody>
              </table>
            </div>
            <form className="add-asset-form" onSubmit={addAsset}>
              <span className="form-label">ADD ASSET</span>
              <input aria-label="Asset name" placeholder="Name" maxLength="80" value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} required />
              <input aria-label="Asset cost" placeholder="Cost $" type="number" min="1" value={draft.cost} onChange={(event) => setDraft({ ...draft, cost: event.target.value })} required />
              <input aria-label="Expected return" placeholder="Return $" type="number" min="0" value={draft.expected_return} onChange={(event) => setDraft({ ...draft, expected_return: event.target.value })} required />
              <button className="add-button" type="submit" aria-label="Add asset" title="Add asset" disabled={assets.length >= 25}>+</button>
            </form>
            <form className="solver-form" onSubmit={runOptimization}>
              <div className="algorithm-choice" role="group" aria-label="Choose algorithm">
                <button className={algorithm === 'dp' ? 'active' : ''} type="button" onClick={() => setAlgorithm('dp')}><span className="choice-mark">01</span> Dynamic programming</button>
                <button className={algorithm === 'brute_force' ? 'active' : ''} type="button" onClick={() => setAlgorithm('brute_force')}><span className="choice-mark">02</span> Brute force</button>
              </div>
              <button className="run-button" type="submit" disabled={busy !== '' || assets.length === 0}>
                {busy === 'optimize' ? 'Calculating…' : 'Find optimal portfolio'} <span aria-hidden="true">↗</span>
              </button>
            </form>
          </div>

          <div className="result-column">
            <section className="result-panel">
              <div className="panel-heading"><div><span className="section-index">02</span><h2>Solution</h2></div><span className="live-label"><span className="live-dot" /> {result ? 'COMPUTED' : 'READY'}</span></div>
              {result ? <>
                <div className="result-amount"><span>MAX EXPECTED RETURN</span><strong>${result.max_expected_return.toLocaleString()}</strong><small>${result.total_cost.toLocaleString()} allocated of ${Number(budget).toLocaleString()}</small></div>
                <div className="metrics-row"><div><span>EXECUTION</span><strong>{formatMs(result.execution_time_ms)}</strong></div><div><span>TIME</span><strong>{result.time_complexity}</strong></div><div><span>SPACE</span><strong>{result.space_complexity}</strong></div></div>
                <div className="selected-assets"><span className="form-label">SELECTED ASSETS</span>{result.selected_assets.length ? result.selected_assets.map((asset, index) => <div className="selected-row" key={`${asset.name}-${index}`}><span>{asset.name}</span><span>${asset.cost} <b>→</b> +${asset.expected_return}</span></div>) : <p className="muted-copy">No assets fit this budget.</p>}</div>
              </> : <div className="empty-result"><span className="empty-symbol">↗</span><p>Run an algorithm to see the best return, selected assets, and measured execution time.</p></div>}
            </section>
            <div className="complexity-note"><span className="note-icon">i</span><p><strong>Model assumptions</strong>Returns and costs are integer inputs. DP runs in $O(NB)$ time and uses $O(B)$ working memory for reconstruction.</p></div>
          </div>
        </section>

        <section className="benchmark-section">
          <div className="benchmark-header"><div><span className="section-index">03</span><h2>Growth of computation</h2><p>Same generated assets, increasing portfolio size. Runtime on a logarithmic scale.</p></div>
            <div className="benchmark-controls"><label htmlFor="max-assets">MAX N</label><input id="max-assets" type="number" min="5" max="23" step="2" value={maxAssets} onChange={(event) => setMaxAssets(event.target.value)} /><button className="benchmark-button" type="button" onClick={runBenchmark} disabled={busy !== ''}>{busy === 'benchmark' ? 'Measuring…' : 'Run benchmark'} <span>↗</span></button></div>
          </div>
          <div className="chart-panel">
            {benchmark.length ? <ResponsiveContainer width="100%" height="100%"><LineChart data={benchmark} margin={{ top: 14, right: 20, bottom: 4, left: 10 }}>
              <CartesianGrid strokeDasharray="3 5" vertical={false} stroke="#dce0d7" />
              <XAxis dataKey="n" tickLine={false} axisLine={{ stroke: '#aeb5a9' }} tick={{ fill: '#697167', fontSize: 11 }} label={{ value: 'Number of assets (N)', position: 'insideBottom', offset: -1, fill: '#697167', fontSize: 11 }} />
              <YAxis scale="log" domain={[0.001, 'auto']} allowDataOverflow={false} tickLine={false} axisLine={false} tick={{ fill: '#697167', fontSize: 11 }} tickFormatter={(value) => value >= 1 ? `${value.toFixed(0)}` : value.toPrecision(1)} label={{ value: 'Execution time (ms, log)', angle: -90, position: 'insideLeft', fill: '#697167', fontSize: 11 }} />
              <Tooltip formatter={(value) => formatMs(Number(value))} labelFormatter={(label) => `N = ${label} assets`} contentStyle={{ border: '1px solid #dce0d7', borderRadius: 4, fontSize: 12 }} />
              <Legend verticalAlign="top" align="right" height={34} iconType="circle" wrapperStyle={{ fontSize: 11 }} />
              <Line name="Brute force · O(2^N)" type="monotone" dataKey="brute_force_ms" stroke="#d6653e" strokeWidth={2.5} dot={{ r: 3, fill: '#d6653e' }} activeDot={{ r: 5 }} />
              <Line name="Dynamic programming · O(NB)" type="monotone" dataKey="dp_ms" stroke="#246b62" strokeWidth={2.5} dot={{ r: 3, fill: '#246b62' }} activeDot={{ r: 5 }} />
            </LineChart></ResponsiveContainer> : <div className="chart-empty"><span className="chart-axis">↗</span><strong>Measure the growth curve</strong><span>Benchmark sizes from N = 5 to {maxAssets} assets</span></div>}
          </div>
          <div className="chart-footnote"><span>EMPIRICAL RUNTIME · PERF_COUNTER · LOG Y-AXIS</span><span>Brute force capped at N ≤ 23</span></div>
        </section>

        {error && <div className="error-banner" role="alert"><strong>Request failed</strong><span>{error}</span><button type="button" aria-label="Dismiss error" onClick={() => setError('')}>×</button></div>}
        <footer className="footer"><span>PORTFOLIO LAB <b>·</b> DAA COURSE PROJECT</span><span>Measurements vary by machine and workload.</span></footer>
      </main>
    </div>
  );
}
