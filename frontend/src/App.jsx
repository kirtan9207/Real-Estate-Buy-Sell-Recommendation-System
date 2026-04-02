import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, ScatterChart, Scatter 
} from 'recharts';
import { 
  Building2, TrendingUp, Search, Map as MapIcon, 
  LayoutDashboard, Settings, Globe, Target, DollarSign, Activity, 
  ShieldAlert, User, Menu, FileText, Clock, ArrowUpRight, Scale, 
  Filter, Download, ChevronRight, MapPin, Zap
} from 'lucide-react';
import { MapContainer, TileLayer, Circle, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const API_BASE = 'http://localhost:8000';
const COLORS = ['#2563eb', '#8b5cf6', '#10b981', '#f59e0b', '#dc2626'];

function App() {
  const [view, setView] = useState('overview');
  const [stats, setStats] = useState({ kpis: {}, trends: [], clusters: {} });
  const [locations, setLocations] = useState([]);
  const [undervalued, setUndervalued] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recs, setRecs] = useState([]);
  const [activeProperty, setActiveProperty] = useState(null);
  const [sellSignal, setSellSignal] = useState(null);
  const [roiAnalysis, setRoiAnalysis] = useState(null);

  // Form states
  const [valuationData, setValuationData] = useState({
    sqft: 1800, bedrooms: 3, bathrooms: 2, age: 3, amenities: 8, metro_dist: 1.2,
    location_id: 0, builder_id: 1, type_id: 0, furnish_id: 1, listing_type_id: 0, q_score: 0.8
  });

  const [recFilter, setRecFilter] = useState({ budget: 15000000, location: 'Whitefield' });

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const { data: s } = await axios.get(`${API_BASE}/market-stats`);
      setStats(s);
      const { data: l } = await axios.get(`${API_BASE}/locations`);
      setLocations(l);
      const { data: uv } = await axios.get(`${API_BASE}/undervalued`);
      setUndervalued(uv);
      if (uv.length > 0) setActiveProperty(uv[0].property_id);
    } catch (e) {
      console.error("Market data sync failed", e);
    }
  };

  useEffect(() => {
    if (activeProperty) {
      fetchPropertyIntel(activeProperty);
    }
  }, [activeProperty]);

  const fetchPropertyIntel = async (pid) => {
    try {
      const { data: r } = await axios.get(`${API_BASE}/roi?property_id=${pid}`);
      setRoiAnalysis(r);
      const { data: s } = await axios.get(`${API_BASE}/sell-signal?property_id=${pid}`);
      setSellSignal(s);
    } catch (e) { console.error(e); }
  };

  const handleValuation = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/predict`, valuationData);
      setPrediction(res.data);
    } finally { setLoading(false); }
  };

  const handleRecommend = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_BASE}/recommend`, null, { 
        params: { budget: recFilter.budget, location: recFilter.location } 
      });
      setRecs(res.data);
    } catch (e) { console.error(e); }
  };

  const SidebarItem = ({ id, icon: Icon, label }) => (
    <div className={`nav-item ${view === id ? 'active' : ''}`} onClick={() => setView(id)}>
      <Icon size={18} /> <span>{label}</span>
    </div>
  );

  const formatPrice = (v) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v);

  return (
    <div className="app-grid">
      <div className="sidebar">
        <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 40, color: 'var(--accent)', fontWeight: 800}}>
           <Globe size={28} /> <span>INTELLIGENCE</span>
        </div>
        
        <div className="nav-group">
          <div className="nav-label">Analytics</div>
          <SidebarItem id="overview" icon={LayoutDashboard} label="Market Overview" />
          <SidebarItem id="heatmap" icon={MapIcon} label="Market Heatmap" />
          <SidebarItem id="segments" icon={Activity} label="Market Segments" />
        </div>

        <div className="nav-group">
          <div className="nav-label">Investment Tools</div>
          <SidebarItem id="predict" icon={Target} label="Price Predictor" />
          <SidebarItem id="recommend" icon={Search} label="Recommendations" />
          <SidebarItem id="roi" icon={Scale} label="ROI Analyzer" />
          <SidebarItem id="sell" icon={Clock} label="Sell Timing" />
        </div>

        <div className="nav-group">
          <div className="nav-label">Reports</div>
          <SidebarItem id="reports" icon={FileText} label="Asset Reports" />
        </div>
      </div>

      <div className="main-view">
        <div className="dashboard-header">
           <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
              <Menu size={20} color="var(--text-dim)" />
              <div style={{fontSize: '0.8rem', color: 'var(--text-dim)'}}>System Status: <span style={{color: 'var(--success)'}}>Operational</span></div>
           </div>
           <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
              <div className="tag tag-accent" style={{display: 'flex', alignItems: 'center', gap: 8}}><TrendingUp size={12}/> MARKET: BULLISH</div>
              <button className="btn-report" onClick={() => window.print()}><Download size={14}/> Export</button>
              <User size={20} />
           </div>
        </div>

        <div className="view-content">
          {view === 'overview' && stats.kpis && (
            <>
              <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Intelligence Dashboard</h1>
              <div className="kpi-row">
                <div className="kpi-card">
                  <div className="kpi-title">AVG MARKET PRICE</div>
                  <div className="kpi-value">{formatPrice(stats.kpis.avg_price || 0)}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-title">TOTAL ASSETS</div>
                  <div className="kpi-value">{(stats.kpis.total_assets || 0).toLocaleString()}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-title">UNDERVALUED TARGETS</div>
                  <div className="kpi-value" style={{color: 'var(--success)'}}>{stats.kpis.undervalued_count || 0}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-title">BEST ROI REGION</div>
                  <div className="kpi-value">{stats.kpis.high_roi_region || 'N/A'}</div>
                </div>
              </div>

              <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 32}}>
                <div className="kpi-card" style={{height: 400}}>
                  <div className="kpi-title">REGIONAL ROI VS TRENDS</div>
                  <ResponsiveContainer width="100%" height="90%">
                    <AreaChart data={locations}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                      <XAxis dataKey="location" axisLine={false} tickLine={false} tick={{fill: '#888', fontSize: 10}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#888', fontSize: 10}} />
                      <Tooltip contentStyle={{background: '#141414', border: '1px solid #222'}} />
                      <Area type="monotone" dataKey="roi" stroke="#2563eb" fillOpacity={0.2} fill="#2563eb" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="kpi-card">
                  <div className="kpi-title">SEGMENTATION DISTRIBUTION</div>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie 
                        data={Object.entries(stats.clusters || {}).map(([k,v]) => ({name: k, value: v}))} 
                        innerRadius={60} 
                        outerRadius={80} 
                        paddingAngle={5} 
                        dataKey="value"
                      >
                        {COLORS.map((c,i)=><Cell key={i} fill={c}/>)}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {view === 'segments' && (
            <>
              <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Market Segmentation</h1>
              <div className="kpi-row">
                 {Object.entries(stats.clusters || {}).map(([k,v], i) => (
                   <div key={k} className="kpi-card">
                      <div className="kpi-title">CLUSTER {k} AVG PRICE</div>
                      <div className="kpi-value">{formatPrice(v)}</div>
                      <div style={{marginTop: 8, fontSize: '0.7rem', color: COLORS[i]}}>Segment Alpha Group</div>
                   </div>
                 ))}
              </div>
              <div className="kpi-card" style={{height: 500}}>
                 <div className="kpi-title">SEGMENT PRICE DISPERSION</div>
                 <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={locations}>
                       <XAxis dataKey="location" axisLine={false} tickLine={false} tick={{fill: '#888', fontSize: 10}}/>
                       <YAxis axisLine={false} tickLine={false} tick={{fill: '#888', fontSize: 10}}/>
                       <Tooltip cursor={{fill: '#1a1a1a'}} contentStyle={{background: '#141414', border: '1px solid #222'}} />
                       <Bar dataKey="price" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                 </ResponsiveContainer>
              </div>
            </>
          )}

          {view === 'heatmap' && (
            <div style={{height: 'calc(100vh - 150px)', borderRadius: 20, overflow: 'hidden', border: '1px solid #222'}}>
               <MapContainer center={[12.9716, 77.5946]} zoom={11} style={{height:'100%', width:'100%'}}>
                  <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                  {locations.map((loc, i) => (
                     <Circle key={i} center={[loc.latitude, loc.longitude]} radius={1500} pathOptions={{fillColor: loc.roi > 12 ? 'var(--success)' : 'var(--accent)', color: 'transparent', fillOpacity: 0.6}}>
                        <Popup>
                           <div style={{background:'#141414', color:'#fff', padding:10, minWidth: 200}}>
                              <h4 style={{marginBottom: 8}}>{loc.location}</h4>
                              <div style={{display:'flex', justifyContent:'space-between', fontSize: '0.8rem', marginBottom: 4}}><span style={{color:'#888'}}>Avg Price:</span> <span>{formatPrice(loc.price)}</span></div>
                              <div style={{display:'flex', justifyContent:'space-between', fontSize: '0.8rem', marginBottom: 4}}><span style={{color:'#888'}}>Expected ROI:</span> <span style={{color:'var(--success)'}}>{loc.roi.toFixed(1)}%</span></div>
                           </div>
                        </Popup>
                     </Circle>
                  ))}
               </MapContainer>
            </div>
          )}

          {view === 'predict' && (
            <div style={{maxWidth: '1000px', margin: 'auto'}}>
              <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Price Predictor</h1>
              <div className="kpi-card" style={{marginBottom: 40}}>
                 <form onSubmit={handleValuation} style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24}}>
                    <div><div className="kpi-title">SQFT</div><input type="number" className="form-input" value={valuationData.sqft} onChange={e=>setValuationData({...valuationData, sqft: parseInt(e.target.value)})}/></div>
                    <div><div className="kpi-title">BEDROOMS</div><input type="number" className="form-input" value={valuationData.bedrooms} onChange={e=>setValuationData({...valuationData, bedrooms: parseInt(e.target.value)})}/></div>
                    <div><div className="kpi-title">LOCATION ID</div><input type="number" className="form-input" value={valuationData.location_id} onChange={e=>setValuationData({...valuationData, location_id: parseInt(e.target.value)})}/></div>
                    <div><div className="kpi-title">QUALITY SCORE</div><input type="number" step="0.1" className="form-input" value={valuationData.q_score} onChange={e=>setValuationData({...valuationData, q_score: parseFloat(e.target.value)})}/></div>
                    <button type="submit" className="btn-primary" style={{gridColumn: '1 / -1'}} disabled={loading}>{loading ? 'PROCESSING...' : 'RUN ANALYTIC REPORT'}</button>
                 </form>
              </div>
              {prediction && (
                <div className="valuation-report">
                   <div className="report-section">
                      <div className="kpi-title">PREDICTED ASSET VALUE</div>
                      <div style={{fontSize: '3.5rem', fontWeight: 900}}>{formatPrice(prediction.valuation.predicted_price)}</div>
                      <div style={{display:'flex', gap: 12, marginTop: 12}}>
                         <div className="tag tag-accent">ROI FORECAST: {prediction.valuation.roi_forecast}%</div>
                      </div>
                      <div style={{marginTop: 32, padding: 20, background: '#000', border: '1px solid #222', borderRadius: 12}}>
                         <h4 style={{marginBottom: 8}}>Investment Logic</h4>
                         <p style={{fontSize: '0.9rem', color: 'var(--text-dim)'}}>{prediction.investment.logic}</p>
                      </div>
                   </div>
                </div>
              )}
            </div>
          )}

          {view === 'recommend' && (
            <>
              <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Smart Recommendations</h1>
              <div className="kpi-card" style={{marginBottom: 32}}>
                 <form onSubmit={handleRecommend} style={{display: 'flex', gap: 16, alignItems: 'flex-end'}}>
                    <div style={{flex: 1}}><div className="kpi-title">BUDGET (INR)</div><input type="number" className="form-input" value={recFilter.budget} onChange={e=>setRecFilter({...recFilter, budget: parseInt(e.target.value)})}/></div>
                    <div style={{flex: 1}}><div className="kpi-title">LOCATION</div><input type="text" className="form-input" value={recFilter.location} onChange={e=>setRecFilter({...recFilter, location: e.target.value})}/></div>
                    <button type="submit" className="btn-primary" style={{height: 42}}>SEARCH DEALS</button>
                 </form>
              </div>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 24}}>
                 {recs.map(rec => (
                   <div key={rec.property_id} className="kpi-card deal-card">
                      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 16}}>
                         <div style={{fontWeight: 700}}>{rec.location}</div>
                         <div className="badge tag-success">{rec.property_type}</div>
                      </div>
                      <div style={{fontSize: '1.5rem', fontWeight: 800, marginBottom: 8}}>{formatPrice(rec.price)}</div>
                      <div style={{color: 'var(--text-dim)', fontSize: '0.8rem'}}>Sqft: {rec.sqft} | Beds: {rec.bedrooms}</div>
                      <div style={{marginTop: 16, display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #222', paddingTop: 16}}>
                         <div><div className="kpi-title">ROI</div><div style={{color: 'var(--success)', fontWeight: 700}}>{rec.roi}%</div></div>
                         <div><div className="kpi-title">TREND</div><div style={{color: 'var(--accent)', fontWeight: 700}}>HIGH</div></div>
                      </div>
                   </div>
                 ))}
              </div>
            </>
          )}

          {view === 'roi' && roiAnalysis && (
            <>
              <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>ROI Analysis</h1>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 32}}>
                 <div className="kpi-card">
                    <div className="kpi-title">SELECTED ASSET INDEX</div>
                    <select className="form-input" style={{width: '100%', marginBottom: 24}} value={activeProperty} onChange={e=>setActiveProperty(e.target.value)}>
                       {undervalued.map(u => <option key={u.property_id} value={u.property_id}>{u.property_id} ({u.location})</option>)}
                    </select>
                    <div style={{padding: 24, background: '#000', borderRadius: 12}}>
                       <div className="kpi-title">ANNUALIZED ROI</div>
                       <div style={{fontSize: '3rem', fontWeight: 900, color: 'var(--success)'}}>{roiAnalysis.expected_roi}%</div>
                       <div style={{marginTop: 16, color: 'var(--text-dim)'}}>Trend Signal: {roiAnalysis.appreciation_trend}</div>
                    </div>
                 </div>
                 <div className="kpi-card">
                    <div className="kpi-title">PROFITABILITY METRICS</div>
                    <div className="kpi-row" style={{marginTop: 24}}>
                       <div className="kpi-card"><div className="kpi-title">RENTAL YIELD</div><div className="kpi-value">{roiAnalysis.rental_yield}%</div></div>
                       <div className="kpi-card"><div className="kpi-title">INVESTMENT SCORE</div><div className="kpi-value">{roiAnalysis.investment_score}/10</div></div>
                    </div>
                 </div>
              </div>
            </>
          )}

          {view === 'sell' && sellSignal && (
            <div style={{maxWidth: 800, margin: 'auto'}}>
              <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Sell Timing Intelligence</h1>
              <div className="kpi-card" style={{borderLeft: `8px solid ${sellSignal.signal === 'SELL' ? 'var(--red)' : 'var(--success)'}`}}>
                 <div style={{fontSize: '5rem', fontWeight: 900}}>{sellSignal.signal}</div>
                 <h3 style={{marginTop: 24, marginBottom: 12}}>Strategic Explanation</h3>
                 <p style={{lineHeight: 1.6, color: 'var(--text-dim)'}}>{sellSignal.explanation}</p>
              </div>
            </div >
          )}

          {view === 'reports' && (
             <>
               <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Asset Reports</h1>
               <div className="kpi-card">
                  <table style={{width: '100%', borderCollapse: 'collapse'}}>
                     <thead>
                        <tr style={{borderBottom: '1px solid #222'}}>
                           <th style={{padding: 16, textAlign: 'left', color: 'var(--text-dim)'}}>PROPERTY ID</th>
                           <th style={{padding: 16, textAlign: 'left', color: 'var(--text-dim)'}}>LOCATION</th>
                           <th style={{padding: 16, textAlign: 'left', color: 'var(--text-dim)'}}>PRICE</th>
                           <th style={{padding: 16, textAlign: 'left', color: 'var(--text-dim)'}}>ROI</th>
                           <th style={{padding: 16, textAlign: 'left', color: 'var(--text-dim)'}}>ACTION</th>
                        </tr>
                     </thead>
                     <tbody>
                        {undervalued.map(u => (
                          <tr key={u.property_id} style={{borderBottom: '1px solid #1a1a1a'}}>
                             <td style={{padding: 16}}>{u.property_id}</td>
                             <td style={{padding: 16}}>{u.location}</td>
                             <td style={{padding: 16}}>{formatPrice(u.price)}</td>
                             <td style={{padding: 16, color: 'var(--success)'}}>{u.roi}%</td>
                             <td style={{padding: 16}}><button className="btn-report" onClick={() => {setActiveProperty(u.property_id); setView('roi');}}>VIEW ANALYSIS</button></td>
                          </tr>
                        ))}
                     </tbody>
                  </table>
               </div>
             </>
          )}
        </div>
      </div>

      <style jsx>{`
        .form-input { 
          background: #000; border: 1px solid #222; color: #fff; padding: 8px 12px; border-radius: 6px; width: 100%; transition: border 0.3s;
        }
        .form-input:focus { border-color: var(--accent); outline: none; }
        .deal-card:hover { border-color: var(--accent); transform: translateY(-4px); }
        .view-content { animation: fadeIn 0.4s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}

export default App;
