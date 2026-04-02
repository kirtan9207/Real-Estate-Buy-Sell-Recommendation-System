import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, ScatterChart, Scatter 
} from 'recharts';
import { 
  Building2, TrendingUp, Search, Home, Map as MapIcon, 
  LayoutDashboard, Settings, AlertTriangle, CheckCircle, 
  BarChart3, Globe, Zap, Target, DollarSign, Activity, 
  ShieldAlert, User, Menu, Search as SearchIcon, FileText, 
  Clock, ArrowUpRight, Scale
} from 'lucide-react';
import { MapContainer, TileLayer, Circle, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const COLORS = ['#2563eb', '#8b5cf6', '#10b981', '#f59e0b', '#dc2626'];
const API_BASE = 'http://localhost:8000';

function App() {
  const [view, setView] = useState('overview');
  const [stats, setStats] = useState({});
  const [undervalued, setUndervalued] = useState([]);
  const [locations, setLocations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeProperty, setActiveProperty] = useState(null);
  const [sellSignal, setSellSignal] = useState(null);
  const [roiAnalysis, setRoiAnalysis] = useState(null);

  // Form states
  const [predictForm, setPredictForm] = useState({
    sqft: 1500, bedrooms: 3, bathrooms: 2, balconies: 1, parking: 1, age: 5, floor: 3, total_floors: 10,
    furnished: 1, amenities_count: 5, distance_metro: 2.5, distance_school: 1.0, distance_hospital: 3.0,
    location_encoded: 0, age_bucket_encoded: 1, luxury_score: 0.5, roi: 15.0
  });

  const [recommendForm, setRecommendForm] = useState({
    budget: 8000000, location: 'Riverside', bedrooms: 3, amenities_min: 5, max_distance_metro: 5.0
  });
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const { data: mStats } = await axios.get(`${API_BASE}/market-stats`);
      setStats(mStats);
      const { data: uv } = await axios.get(`${API_BASE}/undervalued`);
      setUndervalued(uv);
      const { data: locs } = await axios.get(`${API_BASE}/locations`);
      setLocations(locs);
      if (uv.length > 0) setActiveProperty(uv[0].property_id);
    } catch (e) {
      console.error("Error fetching data", e);
    }
  };

  useEffect(() => {
    if (activeProperty && (view === 'roi' || view === 'sell')) {
      fetchAnalysis(activeProperty);
    }
  }, [activeProperty, view]);

  const fetchAnalysis = async (pid) => {
    try {
      const { data: r } = await axios.get(`${API_BASE}/roi?property_id=${pid}`);
      setRoiAnalysis(r);
      const { data: s } = await axios.get(`${API_BASE}/sell-signal?property_id=${pid}`);
      setSellSignal(s);
    } catch (e) { console.error(e); }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/predict`, predictForm);
      setPrediction(res.data);
    } finally { setLoading(false); }
  };

  const handleRecommend = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_BASE}/recommend`, recommendForm);
      setRecs(res.data);
    } catch (e) { console.error(e); }
  };

  const SidebarItem = ({ id, icon: Icon, label }) => (
    <div className={`nav-link ${view === id ? 'active' : ''}`} onClick={() => setView(id)}>
      <Icon size={18} /> {label}
    </div>
  );

  const formatPrice = (val) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <Globe size={24} color="var(--accent)" /> ESTATE INTELLIGENCE
        </div>
        
        <div className="nav-group">
          <div className="nav-label">Analytics</div>
          <SidebarItem id="overview" icon={LayoutDashboard} label="Overview" />
          <SidebarItem id="heatmap" icon={MapIcon} label="Market Heatmap" />
          <SidebarItem id="segments" icon={Activity} label="Market Segments" />
        </div>

        <div className="nav-group">
          <div className="nav-label">Advisory</div>
          <SidebarItem id="predict" icon={Target} label="Price Predictor" />
          <SidebarItem id="recommend" icon={Search} label="Recommendations" />
          <SidebarItem id="roi" icon={Scale} label="ROI Analyzer" />
          <SidebarItem id="sell" icon={Clock} label="Sell Timing" />
        </div>

        <div className="nav-group">
          <div className="nav-label">Resources</div>
          <SidebarItem id="reports" icon={FileText} label="Asset Reports" />
          <SidebarItem id="settings" icon={Settings} label="Settings" />
        </div>
      </div>

      {/* Main Content */}
      <div className="main-area">
        <div className="navbar">
          <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
             <Menu size={20} color="var(--text-secondary)" />
             <div style={{position: 'relative'}}>
                <SearchIcon size={16} color="var(--text-secondary)" style={{position: 'absolute', left: 12, top: 12}} />
                <input type="text" placeholder="Search market, location, or property ID..." className="search-box" style={{paddingLeft: 40}} />
             </div>
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
             <div className="badge badge-green" style={{background: 'rgba(34, 197, 94, 0.05)', display: 'flex', alignItems: 'center', gap: 8}}>
                <TrendingUp size={14} /> MARKET: BULLISH
             </div>
             <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
                <div style={{textAlign: 'right'}}>
                   <div style={{fontSize: '0.8rem', fontWeight: 600}}>System Admin</div>
                   <div style={{fontSize: '0.7rem', color: 'var(--text-secondary)'}}>Standard Account</div>
                </div>
                <User size={28} color="var(--text-secondary)" style={{background: '#18181b', borderRadius: '50%', padding: 4}} />
             </div>
          </div>
        </div>

        <div className="content-wrapper">
          {view === 'overview' && (
            <>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 32}}>
                 <div>
                    <h1 className="dashboard-title" style={{marginBottom: 8}}>Market Intelligence Overview</h1>
                    <p style={{color: 'var(--text-secondary)'}}>Aggregated analytics for major emerging real estate clusters.</p>
                 </div>
                 <div style={{display: 'flex', gap: 12}}>
                    <button className="btn" style={{background: 'transparent', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8}}><FileText size={14}/> Export Report</button>
                    <button className="btn">Invest Now</button>
                 </div>
              </div>

              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-card-title">AVG MARKET PRICE</div>
                  <div className="kpi-card-value">₹ {(stats.avg_price / 10000000).toFixed(2)} Cr</div>
                  <div className="kpi-change up"><TrendingUp size={12}/> 4.82%</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-card-title">ASSETS UNDER ANALYSIS</div>
                  <div className="kpi-card-value">{stats.total_properties}</div>
                  <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 8}}>Live system tracking</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-card-title">UNDERVALUED OPPORTUNITIES</div>
                  <div className="kpi-card-value" style={{color: 'var(--green)'}}>{stats.undervalued_count}</div>
                  <div className="kpi-change up">Strong Buy Signals</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-card-title">MARKET SENTIMENT</div>
                  <div className="kpi-card-value" style={{color: 'var(--accent)'}}>GROWTH</div>
                  <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 8}}>H1 2026 Forecast</div>
                </div>
              </div>

              <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 32}}>
                <div className="panel" style={{height: 400}}>
                  <div className="panel-header"><div className="panel-title">Regional ROI Distribution</div></div>
                  <ResponsiveContainer width="100%" height="90%">
                    <AreaChart data={locations}>
                      <defs>
                        <linearGradient id="colorRoi" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="var(--accent)" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                      <XAxis dataKey="location" axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)', fontSize: 12}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)', fontSize: 12}} />
                      <Tooltip contentStyle={{background: '#18181b', border: '1px solid #27272a'}} />
                      <Area type="monotone" dataKey="roi" stroke="var(--accent)" fillOpacity={1} fill="url(#colorRoi)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="panel">
                  <div className="panel-header"><div className="panel-title">Market Mix</div></div>
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie data={[{name: 'Budget', value: 40}, {name: 'Mid', value: 30}, {name: 'Premium', value: 20}, {name: 'Ultra', value: 10}]} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                        {COLORS.map((c, i) => <Cell key={i} fill={c} />)}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{marginTop: 20}}>
                     {['Budget', 'Mid', 'Premium', 'Ultra'].map((n, i) => (
                       <div key={n} style={{display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.8rem'}}>
                          <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                             <div style={{width: 8, height: 8, background: COLORS[i], borderRadius: '50%'}}></div> {n}
                          </div>
                          <div style={{color: 'var(--text-secondary)'}}>{i * 10 + 20}%</div>
                       </div>
                     ))}
                  </div>
                </div>
              </div>
            </>
          )}

          {view === 'roi' && (
            <>
              <h1 className="dashboard-title">ROI Analyzer</h1>
              <div className="panel">
                 <div className="form-label">Select Property for Analysis</div>
                 <select className="form-input" style={{width: 300}} value={activeProperty} onChange={e => setActiveProperty(e.target.value)}>
                    {undervalued.map(u => <option key={u.property_id} value={u.property_id}>{u.property_id} ({u.location})</option>)}
                 </select>
              </div>

              {roiAnalysis && (
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32}}>
                   <div className="panel">
                      <h3 style={{marginBottom: 20}}>Profitability Forecast</h3>
                      <div style={{background: '#09090b', padding: 24, borderRadius: 8, marginBottom: 20}}>
                         <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>EXPECTED 5-YEAR ROI</div>
                         <div style={{fontSize: '3rem', fontWeight: 800, color: 'var(--green)'}}>{roiAnalysis.expected_roi}%</div>
                         <div style={{display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', marginTop: 8}}>
                            <TrendingUp size={16} /> Market Trend: {roiAnalysis.appreciation_trend}
                         </div>
                      </div>
                      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16}}>
                         <div className="kpi-card">
                            <div className="kpi-card-title">RENTAL YIELD</div>
                            <div className="kpi-card-value">{roiAnalysis.rental_yield}%</div>
                         </div>
                         <div className="kpi-card">
                            <div className="kpi-card-title">INVESTMENT SCORE</div>
                            <div className="kpi-card-value" style={{color: 'var(--accent)'}}>{roiAnalysis.investment_score}/10</div>
                         </div>
                      </div>
                   </div>
                   <div className="panel">
                      <h3 style={{marginBottom: 20}}>Appreciation Curve</h3>
                      <ResponsiveContainer width="100%" height={300}>
                         <LineChart data={[
                           {y: 0, p: 0}, {y: 1, p: 15}, {y: 2, p: 45}, {y: 3, p: 85}, {y: 4, p: 120}
                         ]}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                            <XAxis dataKey="y" name="Year" />
                            <YAxis />
                            <Tooltip contentStyle={{background: '#18181b', border: '1px solid #27272a'}} />
                            <Line type="monotone" dataKey="p" stroke="var(--green)" strokeWidth={3} dot={{fill: 'var(--green)'}} />
                         </LineChart>
                      </ResponsiveContainer>
                   </div>
                </div>
              )}
            </>
          )}

          {view === 'sell' && (
             <>
               <h1 className="dashboard-title">Sell Timing Prediction</h1>
               <div className="panel">
                  <div className="form-label">Active Investment Target</div>
                  <select className="form-input" style={{width: 300}} value={activeProperty} onChange={e => setActiveProperty(e.target.value)}>
                    {undervalued.map(u => <option key={u.property_id} value={u.property_id}>{u.property_id} ({u.location})</option>)}
                  </select>
               </div>

               {sellSignal && (
                 <div className="panel" style={{borderLeft: `8px solid ${sellSignal.signal === 'SELL' ? 'var(--red)' : sellSignal.signal === 'BUY' ? 'var(--green)' : 'var(--accent)'}`}}>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
                       <div>
                          <div style={{fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1}}>Prediction Status</div>
                          <div style={{fontSize: '4rem', fontWeight: 900, marginTop: 8}}>{sellSignal.signal}</div>
                       </div>
                       <div style={{maxWidth: 400}}>
                          <h4 style={{marginBottom: 12}}>Reasoning & Strategy</h4>
                          <p style={{color: 'var(--text-secondary)', lineHeight: 1.6}}>{sellSignal.explanation}</p>
                          <button className="btn" style={{marginTop: 24, width: '100%', background: sellSignal.signal === 'SELL' ? 'var(--red)' : 'var(--accent)'}}>
                             {sellSignal.signal === 'SELL' ? 'Liquidate Position' : 'Hold Position'}
                          </button>
                       </div>
                    </div>
                 </div>
               )}
             </>
          )}

          {view === 'heatmap' && (
            <>
              <h1 className="dashboard-title">Geographical Market Intel</h1>
              <div className="panel" style={{height: '600px', padding: 0}}>
                <MapContainer center={[13.0, 77.6]} zoom={12} style={{ height: '100%', width: '100%' }}>
                  <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                  {locations.map((loc, i) => (
                    <Circle 
                      key={i} 
                      center={[loc.latitude, loc.longitude]} 
                      radius={1200} 
                      pathOptions={{
                        fillColor: loc.roi > 20 ? 'var(--green)' : loc.roi > 15 ? 'var(--accent)' : 'var(--gray)',
                        color: 'transparent',
                        fillOpacity: 0.7
                      }}
                    >
                      <Popup>
                        <div style={{background: '#18181b', color: 'white', padding: 12, minWidth: 200}}>
                          <div style={{fontWeight: 700, fontSize: '1rem', borderBottom: '1px solid #27272a', paddingBottom: 8, marginBottom: 8}}>{loc.location}</div>
                          <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 4}}>
                             <span style={{color: '#a1a1aa'}}>Avg Price:</span>
                             <span>{formatPrice(loc.price)}</span>
                          </div>
                          <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 4}}>
                             <span style={{color: '#a1a1aa'}}>Growth Index:</span>
                             <span style={{color: 'var(--green)'}}>{loc.market_trend.toFixed(2)}</span>
                          </div>
                          <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 4}}>
                             <span style={{color: '#a1a1aa'}}>ROI:</span>
                             <span style={{fontWeight: 700}}>{loc.roi.toFixed(1)}%</span>
                          </div>
                          <div className="badge badge-blue" style={{marginTop: 8, width: '100%', textAlign: 'center'}}>{loc.cluster_label}</div>
                        </div>
                      </Popup>
                    </Circle>
                  ))}
                </MapContainer>
              </div>
            </>
          )}

          {view === 'predict' && (
            <div style={{maxWidth: '900px', margin: 'auto'}}>
              <h1 className="dashboard-title">AI Valuer 2.0</h1>
              <div className="panel">
                <form onSubmit={handlePredict}>
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24}}>
                    <div className="form-group">
                      <div className="form-label">Sqft</div>
                      <input type="number" className="form-input" value={predictForm.sqft} onChange={e => setPredictForm({...predictForm, sqft: parseInt(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                      <div className="form-label">Bedrooms</div>
                      <input type="number" className="form-input" value={predictForm.bedrooms} onChange={e => setPredictForm({...predictForm, bedrooms: parseInt(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                      <div className="form-label">Location (ID)</div>
                      <input type="number" className="form-input" value={predictForm.location_encoded} onChange={e => setPredictForm({...predictForm, location_encoded: parseInt(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                      <div className="form-label">Amenities (0-15)</div>
                      <input type="number" className="form-input" value={predictForm.amenities_count} onChange={e => setPredictForm({...predictForm, amenities_count: parseInt(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                      <div className="form-label">Metro Dist (km)</div>
                      <input type="number" className="form-input" value={predictForm.distance_metro} onChange={e => setPredictForm({...predictForm, distance_metro: parseFloat(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                      <div className="form-label">Age (Years)</div>
                      <input type="number" className="form-input" value={predictForm.age} onChange={e => setPredictForm({...predictForm, age: parseInt(e.target.value)})}/>
                    </div>
                  </div>
                  <button type="submit" className="btn" style={{width: '100%', marginTop: 32, padding: 16, fontSize: '1rem'}}>
                     {loading ? 'Processing Model...' : 'Run Valuation Report'}
                  </button>
                </form>
              </div>

              {prediction && (
                <div className="panel" style={{border: '1px solid var(--accent)', background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(9, 9, 11, 0) 100%)'}}>
                   <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                      <div>
                         <div style={{fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase'}}>Projected Fair Market Value</div>
                         <div style={{fontSize: '3.5rem', fontWeight: 900, margin: '8px 0'}}>{formatPrice(prediction.predicted_price)}</div>
                         <div style={{display: 'flex', gap: 16}}>
                            <div className="badge badge-blue">ACCURACY: HIGH</div>
                            <div className="badge badge-green">BUY RECOMMENDATION</div>
                         </div>
                      </div>
                      <div style={{textAlign: 'right', borderLeft: '1px solid var(--border)', paddingLeft: 40}}>
                         <div style={{marginBottom: 16}}>
                            <div style={{fontSize: '0.7rem', color: 'var(--text-secondary)'}}>5-YEAR GROWTH</div>
                            <div style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--green)'}}>+42.5%</div>
                         </div>
                         <div>
                            <div style={{fontSize: '0.7rem', color: 'var(--text-secondary)'}}>VALUATION STATUS</div>
                            <div style={{fontSize: '1.2rem', fontWeight: 700}}>{prediction.valuation_label}</div>
                         </div>
                      </div>
                   </div>
                </div>
              )}
            </div>
          )}

          {view === 'recommend' && (
             <div style={{maxWidth: '1000px', margin: 'auto'}}>
               <h1 className="dashboard-title">Strategic Investment Search</h1>
               <div className="panel">
                  <form onSubmit={handleRecommend} style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr) auto', gap: 16, alignItems: 'flex-end'}}>
                     <div>
                        <div className="form-label">Max Budget</div>
                        <input type="number" className="form-input" value={recommendForm.budget} onChange={e => setRecommendForm({...recommendForm, budget: parseInt(e.target.value)})}/>
                     </div>
                     <div>
                        <div className="form-label">Preferred Location</div>
                        <select className="form-input" value={recommendForm.location} onChange={e => setRecommendForm({...recommendForm, location: e.target.value})}>
                          {locations.map(l => <option key={l.location} value={l.location}>{l.location}</option>)}
                        </select>
                     </div>
                     <div>
                        <div className="form-label">Min Bedrooms</div>
                        <input type="number" className="form-input" value={recommendForm.bedrooms} onChange={e => setRecommendForm({...recommendForm, bedrooms: parseInt(e.target.value)})}/>
                     </div>
                     <div>
                        <div className="form-label">Max Metro Dist</div>
                        <input type="number" className="form-input" value={recommendForm.max_distance_metro} onChange={e => setRecommendForm({...recommendForm, max_distance_metro: parseFloat(e.target.value)})}/>
                     </div>
                     <button type="submit" className="btn" style={{height: 42}}><SearchIcon size={18} /></button>
                  </form>
               </div>

               <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24}}>
                  {recs.map(rec => (
                    <div key={rec.property_id} className="panel" style={{transition: 'transform 0.2s', cursor: 'pointer'}} onClick={() => {setActiveProperty(rec.property_id); setView('roi');}}>
                       <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 16}}>
                          <div style={{fontWeight: 700, fontSize: '1.2rem'}}>{rec.location} <span style={{fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 400}}>#{rec.property_id}</span></div>
                          <div className="badge badge-blue">MATCH: {rec.match_score}%</div>
                       </div>
                       <div style={{fontSize: '2rem', fontWeight: 800, marginBottom: 12}}>{formatPrice(rec.price)}</div>
                       <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, borderTop: '1px solid var(--border)', paddingTop: 16}}>
                          <div style={{textAlign: 'center'}}>
                             <div style={{color: 'var(--text-secondary)', fontSize: '0.65rem'}}>ROI</div>
                             <div style={{color: 'var(--green)', fontWeight: 700}}>{rec.roi}%</div>
                          </div>
                          <div style={{textAlign: 'center'}}>
                             <div style={{color: 'var(--text-secondary)', fontSize: '0.65rem'}}>SQFT</div>
                             <div style={{fontWeight: 700}}>{rec.sqft}</div>
                          </div>
                          <div style={{textAlign: 'center'}}>
                             <div style={{color: 'var(--text-secondary)', fontSize: '0.65rem'}}>GROWTH</div>
                             <div style={{color: 'var(--accent)', fontWeight: 700}}>HIGH</div>
                          </div>
                       </div>
                    </div>
                  ))}
               </div>
             </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
