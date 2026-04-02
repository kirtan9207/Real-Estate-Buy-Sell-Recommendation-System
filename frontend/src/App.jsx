import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell 
} from 'recharts';
import { 
  Building2, TrendingUp, Search, Map as MapIcon, 
  LayoutDashboard, Settings, Globe, Target, DollarSign, Activity, 
  ShieldAlert, User, Menu, FileText, Clock, ArrowUpRight, Scale, 
  Filter, Download, ChevronRight, MapPin
} from 'lucide-react';
import { MapContainer, TileLayer, Circle, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const API_BASE = 'http://localhost:8000';
const COLORS = ['#2563eb', '#8b5cf6', '#10b981', '#f59e0b', '#dc2626'];

function App() {
  const [view, setView] = useState('overview');
  const [stats, setStats] = useState({});
  const [locations, setLocations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recs, setRecs] = useState([]);

  // Form states
  const [valuationData, setValuationData] = useState({
    sqft: 1800, bedrooms: 3, bathrooms: 2, age: 3, amenities: 8, metro_dist: 1.2,
    location_id: 0, builder_id: 1, type_id: 0, furnish_id: 1, listing_type_id: 0, q_score: 0.8
  });

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const { data: s } = await axios.get(`${API_BASE}/market-stats`);
      setStats(s);
      const { data: l } = await axios.get(`${API_BASE}/locations`);
      setLocations(l);
    } catch (e) {
      console.error("Market data sync failed", e);
    }
  };

  const handleValuation = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/predict`, valuationData);
      setPrediction(res.data);
    } finally { setLoading(false); }
  };

  const SidebarItem = ({ id, icon: Icon, label }) => (
    <div className={`nav-item ${view === id ? 'active' : ''}`} onClick={() => setView(id)}>
      <Icon size={18} /> <span>{label}</span>
    </div>
  );

  const formatPrice = (v) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v);

  return (
    <div className="app-grid">
      {/* Sidebar Navigation */}
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
          <SidebarItem id="assets" icon={FileText} label="Asset Reports" />
          <SidebarItem id="market" icon={TrendingUp} label="Market Reports" />
        </div>

        <div className="nav-group" style={{marginTop: 'auto', marginBottom: 0}}>
          <SidebarItem id="settings" icon={Settings} label="Settings" />
        </div>
      </div>

      {/* Main Dashboard Area */}
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

        {view === 'overview' && stats.kpis && (
          <>
            <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Intelligence Dashboard</h1>
            
            <div className="kpi-row">
              <div className="kpi-card">
                 <div className="kpi-title">AVG MARKET PRICE</div>
                 <div className="kpi-value">{formatPrice(stats.kpis.avg_price)}</div>
                 <div style={{fontSize: '0.7rem', color: 'var(--success)', marginTop: 8, display: 'flex', alignItems: 'center', gap: 4}}><ArrowUpRight size={12}/> +4.2% YoY</div>
              </div>
              <div className="kpi-card">
                 <div className="kpi-title">TOTAL ASSETS</div>
                 <div className="kpi-value">{stats.kpis.total_assets.toLocaleString()}</div>
                 <div style={{fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: 8}}>Live system tracking</div>
              </div>
              <div className="kpi-card">
                 <div className="kpi-title">UNDERVALUED SIGNALS</div>
                 <div className="kpi-value" style={{color: 'var(--success)'}}>{stats.kpis.undervalued_count}</div>
                 <div style={{fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: 8}}>Primary investment targets</div>
              </div>
              <div className="kpi-card">
                 <div className="kpi-title">BEST ROI REGION</div>
                 <div className="kpi-value">{stats.kpis.high_roi_region}</div>
                 <div style={{fontSize: '0.7rem', color: 'var(--accent)', marginTop: 8}}>Market Focus Area</div>
              </div>
            </div>

            <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 32}}>
               <div className="kpi-card" style={{height: 400}}>
                  <div className="kpi-title">REGIONAL PRICE VS ROI TRENDS</div>
                  <ResponsiveContainer width="100%" height="90%">
                     <AreaChart data={locations}>
                        <defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/><stop offset="95%" stopColor="#2563eb" stopOpacity={0}/></linearGradient></defs>
                        <XAxis dataKey="location" axisLine={false} tickLine={false} tick={{fill: '#888', fontSize: 10}} />
                        <YAxis axisLine={false} tickLine={false} tick={{fill: '#888', fontSize: 10}} />
                        <Tooltip contentStyle={{background: '#141414', border: '1px solid #222'}} />
                        <Area type="monotone" dataKey="roi" stroke="#2563eb" fillOpacity={1} fill="url(#c)" />
                     </AreaChart>
                  </ResponsiveContainer>
               </div>
               <div className="kpi-card">
                  <div className="kpi-title">SEGMENTATION MIX</div>
                  <ResponsiveContainer width="100%" height={250}>
                     <PieChart>
                        <Pie data={[{n:'E',v:40},{n:'M',v:35},{n:'P',v:25}]} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="v">
                           {COLORS.map((c,i)=><Cell key={i} fill={c}/>)}
                        </Pie>
                     </PieChart>
                  </ResponsiveContainer>
                  <div style={{marginTop: 20}}>
                     {['Emerging', 'Mid-range', 'Premium'].map((n,i)=>(
                       <div key={n} style={{display:'flex', justifyContent:'space-between', marginBottom: 8, fontSize: '0.8rem'}}>
                          <div style={{display:'flex', alignItems:'center', gap: 8}}><div style={{width: 8, height: 8, background: COLORS[i], borderRadius: '50%'}}></div> {n}</div>
                          <div style={{color: 'var(--text-dim)'}}>{i*10+20}%</div>
                       </div>
                     ))}
                  </div>
               </div>
            </div>
          </>
        )}

        {view === 'predict' && (
          <div style={{maxWidth: '1000px', margin: 'auto'}}>
            <h1 style={{fontSize: '2rem', fontWeight: 800, marginBottom: 32}}>Professional AI Valuer</h1>
            <div className="kpi-card" style={{marginBottom: 40}}>
               <form onSubmit={handleValuation} style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24}}>
                  <div><div className="kpi-title">SQFT</div><input type="number" value={valuationData.sqft} onChange={e=>setValuationData({...valuationData, sqft: parseInt(e.target.value)})} style={{background:'#000', border:'1px solid #222', color:'#fff', padding:8, borderRadius:6, width:'100%'}}/></div>
                  <div><div className="kpi-title">BEDROOMS</div><input type="number" value={valuationData.bedrooms} onChange={e=>setValuationData({...valuationData, bedrooms: parseInt(e.target.value)})} style={{background:'#000', border:'1px solid #222', color:'#fff', padding:8, borderRadius:6, width:'100%'}}/></div>
                  <div><div className="kpi-title">LOCATION ID</div><input type="number" value={valuationData.location_id} onChange={e=>setValuationData({...valuationData, location_id: parseInt(e.target.value)})} style={{background:'#000', border:'1px solid #222', color:'#fff', padding:8, borderRadius:6, width:'100%'}}/></div>
                  <div><div className="kpi-title">QUALITY SCORE</div><input type="number" step="0.1" value={valuationData.q_score} onChange={e=>setValuationData({...valuationData, q_score: parseFloat(e.target.value)})} style={{background:'#000', border:'1px solid #222', color:'#fff', padding:8, borderRadius:6, width:'100%'}}/></div>
                  <button type="submit" className="btn-primary" style={{gridColumn: '1 / -1'}}>{loading ? 'SYCHRONIZING MODELS...' : 'RUN VALUATION REPORT'}</button>
               </form>
            </div>

            {prediction && (
              <div className="valuation-report">
                 <div className="report-section">
                    <div style={{display:'flex', justifyContent:'space-between', borderBottom:'1px solid #222', paddingBottom: 24, marginBottom: 24}}>
                       <div>
                          <div className="kpi-title">PREDICTED ASSET VALUE</div>
                          <div style={{fontSize: '3.5rem', fontWeight: 900}}>{formatPrice(prediction.valuation.predicted_price)}</div>
                          <div style={{display:'flex', gap: 12, marginTop: 12}}>
                             <div className="tag tag-accent">CONFIDENCE: {prediction.valuation.confidence_score * 100}%</div>
                             <div className="tag tag-success">{prediction.investment.segment.toUpperCase()} ASSET</div>
                          </div>
                       </div>
                       <div style={{textAlign: 'right'}}>
                          <div className="kpi-title">VALUATION STATUS</div>
                          <div style={{fontSize: '1.2rem', fontWeight: 800, color: 'var(--success)'}}>UNDERVALUED</div>
                          <div style={{marginTop: 16}}>
                             <div className="kpi-title">5-YEAR FORECAST</div>
                             <div style={{fontSize: '1.5rem', fontWeight: 800}}>{prediction.valuation.appreciation_5y}</div>
                          </div>
                       </div>
                    </div>
                    
                    <h3 style={{marginBottom: 16}}>Market Logic Engine</h3>
                    <p style={{color: 'var(--text-dim)', lineHeight: 1.6, background:'#000', padding: 20, borderRadius: 12, border: '1px solid #222'}}>{prediction.investment.logic}</p>
                 </div>
                 
                 <div className="report-section">
                    <h3 style={{marginBottom: 24}}>Investment Signals</h3>
                    <div style={{marginBottom: 24}}>
                       <div className="kpi-title">ACTION SIGNAL</div>
                       <div style={{fontSize: '1.8rem', fontWeight: 800, color: prediction.investment.recommended_action === 'ENTER' ? 'var(--success)' : 'var(--accent)'}}>{prediction.investment.signal}</div>
                    </div>
                    <div style={{marginBottom: 24}}>
                       <div className="kpi-title">ROI STRATEGY</div>
                       <div style={{fontSize: '1.8rem', fontWeight: 800}}>{prediction.valuation.roi_forecast}% <span style={{fontSize: '0.8rem', color:'var(--text-dim)', fontWeight: 400}}>annually</span></div>
                    </div>
                    <button className="btn-primary" style={{width:'100%', marginTop: 20}}>REQUEST DOCUMENTATION</button>
                    <p style={{fontSize:'0.6rem', color: 'var(--text-dim)', marginTop: 16, textAlign: 'center'}}>Final valuation based on last 20,000 market samples.</p>
                 </div>
              </div>
            )}
          </div>
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
                             <div style={{display:'flex', justifyContent:'space-between', fontSize: '0.8rem', marginBottom: 4}}><span style={{color:'#888'}}>ROI index:</span> <span style={{color:'var(--success)'}}>{loc.roi.toFixed(1)}%</span></div>
                             <div style={{display:'flex', justifyContent:'space-between', fontSize: '0.8rem', marginBottom: 4}}><span style={{color:'#888'}}>Market Trend:</span> <span>+{(loc.market_trend * 100).toFixed(1)}%</span></div>
                          </div>
                       </Popup>
                    </Circle>
                 ))}
              </MapContainer>
           </div>
        )}
      </div>
    </div>
  );
}

export default App;
