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
  ShieldAlert, User, Menu, Search as SearchIcon
} from 'lucide-react';
import { MapContainer, TileLayer, Circle, Popup, Marker } from 'react-leaflet';
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
    } catch (e) {
      console.error("Error fetching data", e);
    }
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
          <SidebarItem id="roi" icon={TrendingUp} label="ROI Analyzer" />
          <SidebarItem id="sell" icon={ShieldAlert} label="Sell Timing" />
        </div>

        <div className="nav-group" style={{marginTop: 'auto'}}>
          <SidebarItem id="settings" icon={Settings} label="Settings" />
        </div>
      </div>

      {/* Main Content */}
      <div className="main-area">
        <div className="navbar">
          <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
             <Menu size={20} color="var(--text-secondary)" />
             <input type="text" placeholder="Search market, location, or property ID..." className="search-box" />
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
             <div style={{display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.8rem', color: 'var(--text-secondary)'}}>
                <div style={{width: 8, height: 8, borderRadius: '50%', background: 'var(--green)'}}></div>
                Market Status: Bullish
             </div>
             <User size={20} color="var(--text-secondary)" />
          </div>
        </div>

        <div className="content-wrapper">
          {view === 'overview' && (
            <>
              <h1 className="dashboard-title">Market Overview</h1>
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-card-title">AVG MARKET PRICE</div>
                  <div className="kpi-card-value">₹ {(stats.avg_price / 10000000).toFixed(2)} Cr</div>
                  <div className="kpi-change up"><TrendingUp size={12}/> 4.2% YoY</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-card-title">PROPERTIES ANALYZED</div>
                  <div className="kpi-card-value">{stats.total_properties}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-card-title">UNDERVALUED COUNT</div>
                  <div className="kpi-card-value" style={{color: 'var(--green)'}}>{stats.undervalued_count}</div>
                  <div className="kpi-change up">Primary Opportunity</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-card-title">BEST ROI REGION</div>
                  <div className="kpi-card-value" style={{color: 'var(--accent)'}}>{stats.best_roi_location}</div>
                </div>
              </div>

              <div className="panel" style={{height: 400}}>
                <div className="panel-header"><div className="panel-title">ROI by Location (Projected)</div></div>
                <ResponsiveContainer width="100%" height="90%">
                  <BarChart data={locations}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="location" axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)', fontSize: 12}} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)', fontSize: 12}} />
                    <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{background: '#18181b', border: '1px solid #27272a', borderRadius: '4px'}} />
                    <Bar dataKey="roi" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="panel">
                <div className="panel-header"><div className="panel-title">Top Undervalued Assets</div></div>
                <table className="data-table">
                  <thead>
                     <tr><th>ID</th><th>Location</th><th>Price</th><th>Expected ROI</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                     {undervalued.map(item => (
                       <tr key={item.property_id}>
                         <td>{item.property_id}</td>
                         <td>{item.location}</td>
                         <td>{formatPrice(item.price)}</td>
                         <td style={{color: 'var(--green)'}}>{item.roi}%</td>
                         <td><span className="badge badge-green">BUY RECOMMENDATION</span></td>
                       </tr>
                     ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {view === 'heatmap' && (
            <>
              <h1 className="dashboard-title">Location Intelligence Heatmap</h1>
              <div className="panel" style={{height: '600px', padding: 0}}>
                <MapContainer center={[13.0, 77.6]} zoom={12} style={{ height: '100%', width: '100%' }}>
                  <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                  {locations.map((loc, i) => (
                    <Circle 
                      key={i} 
                      center={[loc.latitude, loc.longitude]} 
                      radius={1000} 
                      pathOptions={{
                        fillColor: loc.roi > 15 ? 'var(--green)' : 'var(--accent)',
                        color: 'transparent',
                        fillOpacity: 0.6
                      }}
                    >
                      <Popup>
                        <div style={{background: '#18181b', color: 'white', padding: 8}}>
                          <h3>{loc.location}</h3>
                          <p>Avg Price: {formatPrice(loc.price)}</p>
                          <p>ROI: {loc.roi.toFixed(1)}%</p>
                          <p>Segment: {loc.cluster_label}</p>
                        </div>
                      </Popup>
                    </Circle>
                  ))}
                </MapContainer>
              </div>
            </>
          )}

          {view === 'predict' && (
            <div style={{maxWidth: '800px', margin: 'auto'}}>
              <h1 className="dashboard-title">AI Property Valuation</h1>
              <div className="panel">
                <form onSubmit={handlePredict}>
                  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20}}>
                    <div className="form-group">
                      <div className="form-label">Sqft</div>
                      <input type="number" className="form-input" value={predictForm.sqft} onChange={e => setPredictForm({...predictForm, sqft: parseInt(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                      <div className="form-label">Location (Encode 0-7)</div>
                      <input type="number" className="form-input" value={predictForm.location_encoded} onChange={e => setPredictForm({...predictForm, location_encoded: parseInt(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                      <div className="form-label">Bedrooms</div>
                      <input type="number" className="form-input" value={predictForm.bedrooms} onChange={e => setPredictForm({...predictForm, bedrooms: parseInt(e.target.value)})}/>
                    </div>
                    <div className="form-group">
                       <div className="form-label">Amenities Count</div>
                       <input type="number" className="form-input" value={predictForm.amenities_count} onChange={e => setPredictForm({...predictForm, amenities_count: parseInt(e.target.value)})}/>
                    </div>
                  </div>
                  <button type="submit" className="btn" style={{width: '100%', marginTop: 24, padding: 16}}>Calculate Intrinsic Value</button>
                </form>
              </div>

              {prediction && (
                <div className="panel" style={{border: '1px solid var(--accent)', background: 'rgba(37, 99, 235, 0.05)'}}>
                   <div style={{display: 'flex', justifyContent: 'space-between'}}>
                      <div>
                         <div className="kpi-card-title">PROJECTED MARKET VALUE</div>
                         <div style={{fontSize: '2.5rem', fontWeight: 800}}>{formatPrice(prediction.predicted_price)}</div>
                         <div style={{color: 'var(--text-secondary)', marginTop: 8}}>Range: {formatPrice(prediction.price_range[0])} - {formatPrice(prediction.price_range[1])}</div>
                      </div>
                      <div style={{textAlign: 'right'}}>
                         <div className="badge badge-blue" style={{fontSize: '1rem', padding: '8px 16px'}}>{prediction.valuation_label}</div>
                         <div style={{marginTop: 16, color: 'var(--green)', fontWeight: 700}}>ROI: 14.8% (Estimated)</div>
                      </div>
                   </div>
                </div>
              )}
            </div>
          )}

          {view === 'recommend' && (
             <>
               <h1 className="dashboard-title">Investment Recommendations</h1>
               <div className="panel">
                  <form onSubmit={handleRecommend} style={{display: 'flex', gap: 16, alignItems: 'flex-end'}}>
                     <div style={{flex: 1}}>
                        <div className="form-label">Budget</div>
                        <input type="number" className="form-input" value={recommendForm.budget} onChange={e => setRecommendForm({...recommendForm, budget: parseInt(e.target.value)})}/>
                     </div>
                     <div style={{flex: 1}}>
                        <div className="form-label">Location</div>
                        <select className="form-input" value={recommendForm.location} onChange={e => setRecommendForm({...recommendForm, location: e.target.value})}>
                          {locations.map(l => <option value={l.location}>{l.location}</option>)}
                        </select>
                     </div>
                     <button type="submit" className="btn" style={{padding: '12px 24px'}}>Search Deals</button>
                  </form>
               </div>

               <div className="grid">
                  {recs.map(rec => (
                    <div key={rec.property_id} className="panel">
                       <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 12}}>
                          <div style={{fontWeight: 700, fontSize: '1.2rem'}}>{rec.location}</div>
                          <div className="badge badge-green">SCORE: {rec.match_score}</div>
                       </div>
                       <div style={{fontSize: '1.5rem', fontWeight: 800, marginBottom: 8}}>{formatPrice(rec.price)}</div>
                       <div style={{color: 'var(--text-secondary)', fontSize: '0.8rem'}}>Sqft: {rec.sqft} | Beds: {rec.bedrooms}</div>
                       <div style={{marginTop: 16, color: 'var(--green)', fontWeight: 600}}>Exp. ROI: {rec.roi}%</div>
                    </div>
                  ))}
               </div>
             </>
          )}

          {view === 'segments' && (
             <>
               <h1 className="dashboard-title">Market Segmentation</h1>
               <div className="kpi-grid">
                  <div className="kpi-card"><div className="kpi-card-title">BUDGET DOMINANT</div><div className="kpi-card-value">Industrial Zone</div></div>
                  <div className="kpi-card"><div className="kpi-card-title">PREMIUM HUB</div><div className="kpi-card-value">Downtown</div></div>
                  <div className="kpi-card"><div className="kpi-card-title">EMERGING ALPHA</div><div className="kpi-card-value">Riverside</div></div>
               </div>
               <div className="panel" style={{height: 500}}>
                  <div className="panel-header"><div className="panel-title">Cluster Spread (Price vs ROI)</div></div>
                  <ResponsiveContainer width="100%" height="90%">
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis type="number" dataKey="price" name="Price" axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} />
                      <YAxis type="number" dataKey="roi" name="ROI" axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)'}} />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{background: '#18181b', border: '1px solid #27272a'}} />
                      <Scatter name="Properties" data={undervalued} fill="var(--accent)" />
                    </ScatterChart>
                  </ResponsiveContainer>
               </div>
             </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
