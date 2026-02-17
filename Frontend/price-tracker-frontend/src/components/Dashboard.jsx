// Dashboard.jsx - With Functional Notification Toggle

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import AddProduct from "./AddProduct";
import PriceChart from "./PriceChart";
import DarkModeToggle from "./DarkModeToggle";
import { exportToCSV, exportToJSON, shareToWhatsApp } from "../utils/exportUtils";
import "./dashboard.css";
import "./darkmode.css";
import notificationService from "../services/notificationService";

function Dashboard() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeView, setActiveView] = useState("all");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("recent");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showChart, setShowChart] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    // Check notification permission on load
    checkNotificationStatus();

    fetchProducts();
    const interval = setInterval(fetchProducts, 60000);
    return () => clearInterval(interval);
  }, []);

  // ⭐ Check notification status
  const checkNotificationStatus = () => {
    if (notificationService.isSupported()) {
      const permission = notificationService.getPermission();
      setNotificationsEnabled(permission === "granted");
    }
  };

  // ⭐ Toggle notifications
  const handleToggleNotifications = async () => {
    if (!notificationService.isSupported()) {
      alert("❌ Your browser doesn't support notifications");
      return;
    }

    if (notificationsEnabled) {
      // Can't programmatically disable - show instructions
      alert(
        "ℹ️ To disable notifications:\n\n" +
        "1. Click the lock icon 🔒 in your browser address bar\n" +
        "2. Find 'Notifications'\n" +
        "3. Select 'Block'\n\n" +
        "Or check your browser settings."
      );
    } else {
      // Request permission
      const granted = await notificationService.requestPermission();
      setNotificationsEnabled(granted);
      
      if (granted) {
        // Show test notification
        notificationService.showNotification(
          "🔔 Notifications Enabled!",
          {
            body: "You'll now get instant alerts when prices drop",
            requireInteraction: false
          }
        );
      } else {
        alert(
          "❌ Notification permission denied\n\n" +
          "To enable later, click the lock icon 🔒 in your address bar"
        );
      }
    }
  };

  const fetchProducts = async () => {
    try {
      setError("");
      const token = localStorage.getItem("token");
      
      if (!token) {
        navigate("/login");
        return;
      }

      const res = await API.get("/products");
      
      // Check for new deals and notify
      if (products.length > 0) {
        res.data.forEach(newProduct => {
          const oldProduct = products.find(p => p.id === newProduct.id);
          if (oldProduct && newProduct.price <= newProduct.target_price && 
              oldProduct.price > oldProduct.target_price) {
            if (notificationsEnabled) {
              notificationService.showPriceDropAlert(newProduct);
            }
          }
        });
      }
      
      setProducts(res.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching products:", err);
      
      if (err.response?.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/login");
      } else {
        setError("Failed to load products");
        setLoading(false);
      }
    }
  };

  const deleteProduct = async (id) => {
    if (!window.confirm("Are you sure you want to delete this product?")) {
      return;
    }

    try {
      await API.delete(`/product/${id}`);
      fetchProducts();
    } catch (err) {
      console.error("Error deleting product:", err);
      setError("Failed to delete product");
    }
  };

  const toggleSubscription = async (id) => {
    try {
      await API.post(`/toggle-subscription/${id}`);
      fetchProducts();
    } catch (err) {
      console.error("Error toggling subscription:", err);
      setError("Failed to toggle subscription");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  const openPriceChart = (product) => {
    setSelectedProduct(product);
    setShowChart(true);
  };

  const handleExport = (format) => {
    if (format === "csv") {
      exportToCSV(products);
    } else if (format === "json") {
      exportToJSON(products);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const getFilteredProducts = () => {
    let filtered = products;

    if (activeView === "active") {
      filtered = filtered.filter(p => p.subscribed);
    } else if (activeView === "paused") {
      filtered = filtered.filter(p => !p.subscribed);
    } else if (activeView === "deals") {
      filtered = filtered.filter(p => p.price <= p.target_price);
    }

    if (searchQuery) {
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (sortBy === "price-low") {
      filtered = [...filtered].sort((a, b) => a.price - b.price);
    } else if (sortBy === "price-high") {
      filtered = [...filtered].sort((a, b) => b.price - a.price);
    } else if (sortBy === "discount") {
      filtered = [...filtered].sort((a, b) => 
        ((b.target_price - b.price) / b.target_price) - ((a.target_price - a.price) / a.target_price)
      );
    }

    return filtered;
  };

  const stats = {
    total: products.length,
    active: products.filter(p => p.subscribed).length,
    deals: products.filter(p => p.price <= p.target_price).length,
    totalSavings: products.reduce((sum, p) => sum + Math.max(0, p.target_price - p.price), 0)
  };

  const filteredProducts = getFilteredProducts();

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading your products...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <button 
        className="mobile-menu-btn"
        onClick={toggleSidebar}
        aria-label="Toggle menu"
      >
        {sidebarOpen ? "✕" : "☰"}
      </button>

      {sidebarOpen && (
        <div 
          className="sidebar-overlay"
          onClick={toggleSidebar}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>💰 PriceDrop</h2>
        </div>

        {sidebarOpen && (
          <>
            <div className="user-info">
              <div className="user-avatar">
                {user.name ? user.name[0].toUpperCase() : 'U'}
              </div>
              <div className="user-details">
                <p className="user-name">{user.name}</p>
                <p className="user-email">{user.email}</p>
              </div>
            </div>

            <nav className="sidebar-nav">
              <button 
                className={activeView === "all" ? "active" : ""}
                onClick={() => setActiveView("all")}
              >
                <span className="icon">📦</span>
                <span>All Products</span>
                <span className="badge">{stats.total}</span>
              </button>

              <button 
                className={activeView === "active" ? "active" : ""}
                onClick={() => setActiveView("active")}
              >
                <span className="icon">🔔</span>
                <span>Active Alerts</span>
                <span className="badge">{stats.active}</span>
              </button>

              <button 
                className={activeView === "paused" ? "active" : ""}
                onClick={() => setActiveView("paused")}
              >
                <span className="icon">⏸️</span>
                <span>Paused</span>
                <span className="badge">{stats.total - stats.active}</span>
              </button>

              <button 
                className={activeView === "deals" ? "active" : ""}
                onClick={() => setActiveView("deals")}
              >
                <span className="icon">🎉</span>
                <span>Active Deals</span>
                <span className="badge deals">{stats.deals}</span>
              </button>
            </nav>

            <div className="sidebar-stats">
              <h3>Statistics</h3>
              <div className="stat-item">
                <span>Total Tracked:</span>
                <strong>{stats.total}</strong>
              </div>
              <div className="stat-item">
                <span>Active Deals:</span>
                <strong className="deals-count">{stats.deals}</strong>
              </div>
              <div className="stat-item">
                <span>Total Savings:</span>
                <strong>₹{stats.totalSavings.toFixed(0)}</strong>
              </div>
              
              {/* ⭐ Clickable Notification Toggle */}
              <div 
                className="stat-item notification-toggle"
                onClick={handleToggleNotifications}
                style={{ cursor: 'pointer' }}
                title="Click to manage browser notifications"
              >
              </div>
            </div>



            <button className="logout-btn" onClick={handleLogout}>
              <span className="icon">🚪</span>
              <span>Logout</span>
            </button>
          </>
        )}
      </aside>

      <main className="main-content">
        <div className="content-header">
          <h1>
            {activeView === "all" && "All Products"}
            {activeView === "active" && "Active Alerts"}
            {activeView === "paused" && "Paused Products"}
            {activeView === "deals" && "🎉 Active Deals!"}
          </h1>

          <div className="header-actions">
            <input
              type="text"
              placeholder="🔍 Search products..."
              className="search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />

            <select 
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="recent">Recently Added</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="discount">Best Deals First</option>
            </select>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <AddProduct onProductAdded={fetchProducts} />

        {filteredProducts.length === 0 ? (
          <div className="no-products">
            <div className="no-products-icon">📭</div>
            <h3>No products found</h3>
            <p>
              {searchQuery 
                ? "Try a different search term" 
                : "Add your first product to start tracking prices!"}
            </p>
          </div>
        ) : (
          <div className="products-grid">
            {filteredProducts.map((p) => {
              const discount = p.target_price > 0 
                ? ((p.target_price - p.price) / p.target_price * 100).toFixed(1)
                : 0;
              const isDeal = p.price <= p.target_price;

              return (
                <div key={p.id} className={`product-card ${isDeal ? 'deal-card' : ''}`}>
                  {isDeal && <div className="deal-badge">🎉 Deal Alert!</div>}

                  {p.image && (
                    <div className="product-image-container">
                      <img src={p.image} alt={p.name} className="product-img" />
                    </div>
                  )}

                  <div className="product-info">
                    <h3 className="product-name">{p.name}</h3>

                    <div className="price-section">
                      <div className="price-item">
                        <span className="price-label">Current</span>
                        <span className="price-value current">₹{p.price}</span>
                      </div>
                      <div className="price-item">
                        <span className="price-label">Target</span>
                        <span className="price-value target">₹{p.target_price}</span>
                      </div>
                    </div>

                    {discount > 0 && (
                      <div className="discount-info">
                        <span className="discount-badge">{discount}% off</span>
                        <span className="savings">Save ₹{(p.target_price - p.price).toFixed(0)}</span>
                      </div>
                    )}

                    <div className="product-status">
                      <span className={`status-indicator ${p.subscribed ? 'active' : 'paused'}`}>
                        {p.subscribed ? "🟢 Active" : "🔴 Paused"}
                      </span>
                    </div>

                    <div className="product-actions">
                      <button
                        className="btn btn-chart"
                        onClick={() => openPriceChart(p)}
                      >
                       price chart 📊
                      </button>

                      <button
                        className="btn btn-secondary"
                        onClick={() => toggleSubscription(p.id)}
                      >
                      {p.subscribed ? "Unsubscribe⏸️" : "Subscribe▶️"}
                      </button>

                      <a 
                        href={p.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="btn btn-primary"
                      >
                        Buy 🛒
                      </a>

                      <button
                        className="btn btn-danger"
                        onClick={() => deleteProduct(p.id)}
                      >
                        Delete🗑️
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      <DarkModeToggle />

      {showChart && selectedProduct && (
        <PriceChart
          productId={selectedProduct.id}
          productName={selectedProduct.name}
          targetPrice={selectedProduct.target_price}
          onClose={() => setShowChart(false)}
        />
      )}
    </div>
  );
}

export default Dashboard;