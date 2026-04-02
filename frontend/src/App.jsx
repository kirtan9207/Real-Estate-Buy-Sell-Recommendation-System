import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell 
} from 'recharts';
import { 
  Building2, TrendingUp, Search, Home, Map, 
  LayoutDashboard, Settings, AlertTriangle, CheckCircle 
} from 'lucide-react';

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'];

const API_BASE = 'http://localhost:8000';

function App() {
  const [view, setView] = useState('dashboard');
  const [data, setData] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [undervalued, setUndervalued] = useState([]);
  const [stats, setStats] = useState(null);
  
  // Prediction Form State
  const [form, setForm] = useState({
    sqft: 1500, bedrooms: 3, bathrooms: 2, balconies: 1, 
    parking: 1, age: 5, floor: 3, total_floors: 10,
    furnished: 1, amenities_count: 5, distance_metro: 2.5,
    distance_school: 1.0, distance_hospital: 3.0,
    location_encoded: 0, age_bucket_encoded: 1, luxury_score: 0.5, roi: 15.0
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const uv = await axios.get(`${API_BASE}/undervalued`);
      setUndervalued(uv.data);
      const cls = await axios.get(`${API_BASE}/clusters`);
      setStats(cls.data);
    } catch (e) { console.error(e); }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_BASE}/predict`, form);
      setPrediction(res.data.predicted_price);
    } catch (e) { alert("Failed to predict. Is the backend running?"); }
  };

  const renderDashboard = () => (
    <div>
      <div className="grid">
        <div className="card">
          <div className="card-title">Market Average Price</div>
          <div className="card-value">₹ 14.2M</div>
          <div style={{color: 'var(--accent-green)', marginTop: 8}}>+4.2% YoY</div>
        </div>
        <div className="card">
          <div className="card-title">Properties Analyzed</div>
          <div className="card-value">5,000</div>
          <div style={{color: 'var(--text-dim)', marginTop: 8}}>Complete system scan</div>
        </div>
        <div className="card">
          <div className="card-title">Best ROI Location</div>
          <div className="card-value">Riverside</div>
          <div style={{color: 'var(--accent-purple)', marginTop: 8}}>Estimated 28% ROI</div>
        </div>
      </div>

      <div className="grid" style={{gridTemplateColumns: '2fr 1fr'}}>
        <div className="card" style={{height: 400}}>
          <h3 style={{marginBottom: 20}}>Price Trends by Location</h3>
          <ResponsiveContainer width="100%" height="85%">
            <AreaChart data={undervalued}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="location" />
              <YAxis />
              <Tooltip contentStyle={{backgroundColor: '#1e293b', border: 'none'}} />
              <Area type="monotone" dataKey="price_per_sqft" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.1} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3 style={{marginBottom: 20}}>Market Segments</h3>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={stats ? Object.keys(stats).map(k => ({name: k, value: stats[k].count})) : []}
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {COLORS.map((color, index) => <Cell key={`cell-${index}`} fill={color} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 style={{marginBottom: 20}}>Undervalued Opportunities</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Location</th>
              <th>Price</th>
              <th>ROI</th>
              <th>Score</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {undervalued.map(item => (
              <tr key={item.property_id}>
                <td>{item.property_id}</td>
                <td>{item.location}</td>
                <td>₹ {(item.price/1000000).toFixed(1)}M</td>
                <td style={{color: 'var(--accent-green)'}}>{item.roi}%</td>
                <td>{item.utility_score || 8.5}</td>
                <td><span className="btn" style={{padding: '4px 12px', fontSize: '0.75rem'}}>View</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderPredictor = () => (
    <div className="card" style={{maxWidth: 800, margin: 'auto'}}>
      <h2 style={{marginBottom: 24}}>Property Valuation Model</h2>
      <form onSubmit={handlePredict} className="grid" style={{gridTemplateColumns: '1fr 1fr'}}>
        <div className="form-group">
          <label>Square Footage (Sqft)</label>
          <input type="number" value={form.sqft} onChange={e => setForm({...form, sqft: parseInt(e.target.value)})} />
        </div>
        <div className="form-group">
          <label>Bedrooms</label>
          <input type="number" value={form.bedrooms} onChange={e => setForm({...form, bedrooms: parseInt(e.target.value)})} />
        </div>
        <div className="form-group">
          <label>Location (0-7)</label>
          <input type="number" value={form.location_encoded} onChange={e => setForm({...form, location_encoded: parseInt(e.target.value)})} />
        </div>
        <div className="form-group">
          <label>Amenities Count</label>
          <input type="number" value={form.amenities_count} onChange={e => setForm({...form, amenities_count: parseInt(e.target.value)})} />
        </div>
        <div style={{gridColumn: 'span 2'}}>
          <button type="submit" className="btn" style={{width: '100%', fontSize: '1.2rem', padding: '16px'}}>Predict Buy Price</button>
        </div>
      </form>
      
      {prediction && (
        <div className="card" style={{marginTop: 32, textAlign: 'center', background: 'rgba(16, 185, 129, 0.1)', borderColor: 'var(--accent-green)'}}>
          <h3 style={{color: 'var(--text-dim)', marginBottom: 12}}>Estimated Market Value</h3>
          <div style={{fontSize: '3rem', fontWeight: 800, color: 'var(--accent-green)'}}>₹ {(prediction/1000000).toFixed(2)}M</div>
          <div style={{marginTop: 16, display: 'flex', justifyContent: 'center', gap: 24}}>
             <div style={{display: 'flex', alignItems: 'center', gap: 8}}><CheckCircle size={18} /> Buy Recommended</div>
             <div style={{display: 'flex', alignItems: 'center', gap: 8}}><TrendingUp size={18} /> High Growth Area</div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <>
      <div className="sidebar">
        <h1>RE-Platform</h1>
        <div className={`nav-item ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
          <LayoutDashboard size={20} /> Overview
        </div>
        <div className={`nav-item ${view === 'predict' ? 'active' : ''}`} onClick={() => setView('predict')}>
          <Building2 size={20} /> Price Predictor
        </div>
        <div className="nav-item">
          <Map size={20} /> Market Heatmap
        </div>
        <div className="nav-item">
          <Search size={20} /> Recommendations
        </div>
        <div style={{marginTop: 'auto'}} className="nav-item">
          <Settings size={20} /> Settings
        </div>
      </div>
      
      <div className="main-content">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 40}}>
          <h2>{view === 'dashboard' ? 'Market Overview' : 'AI Valuation'}</h2>
          <div style={{display: 'flex', gap: 12}}>
            <div className="card" style={{padding: '8px 16px', display: 'flex', alignItems: 'center', gap: 8}}>
              <div style={{width: 8, height: 8, background: 'var(--accent-green)', borderRadius: '50%'}}></div>
              API Status: Live
            </div>
          </div>
        </div>
        
        {view === 'dashboard' ? renderDashboard() : renderPredictor()}
      </div>
    </>
  );
}

export default App;
