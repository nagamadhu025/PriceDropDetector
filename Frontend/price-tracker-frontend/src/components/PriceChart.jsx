// PriceChart.jsx - Modern Beautiful Design

import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from "chart.js";
import API from "../services/api";
import "./pricechart.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function PriceChart({ productId, productName, targetPrice, onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPriceHistory();
  }, [productId]);

  const fetchPriceHistory = async () => {
    try {
      setLoading(true);
      const res = await API.get(`/product/${productId}/price-history`);
      setHistory(res.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching price history:", err);
      setError("Failed to load price history");
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="chart-modal-overlay" onClick={onClose}>
        <div className="chart-card" onClick={(e) => e.stopPropagation()}>
          <div className="chart-loading">
            <div className="loading-spinner"></div>
            <p>Loading price history...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-modal-overlay" onClick={onClose}>
        <div className="chart-card" onClick={(e) => e.stopPropagation()}>
          <button className="chart-close-btn" onClick={onClose}>✕</button>
          <div className="chart-error">
            <span className="error-icon">⚠️</span>
            <p>{error}</p>
            <button onClick={onClose} className="error-close-btn">Close</button>
          </div>
        </div>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="chart-modal-overlay" onClick={onClose}>
        <div className="chart-card" onClick={(e) => e.stopPropagation()}>
          <button className="chart-close-btn" onClick={onClose}>✕</button>
          
          <div className="chart-header">
            <h2>📊 Price History</h2>
            <p className="product-name-chart">{productName}</p>
          </div>

          <div className="no-history">
            <div className="no-history-icon">📈</div>
            <h3>No Price History Yet</h3>
            <p>We're tracking this product's price.</p>
            <p>Check back in a few hours to see the price trend!</p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate stats
  const prices = history.map(h => h.price);
  const currentPrice = prices[prices.length - 1];
  const lowestPrice = Math.min(...prices);
  const highestPrice = Math.max(...prices);
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
  const priceChange = prices.length > 1 ? currentPrice - prices[0] : 0;
  const priceChangePercent = prices.length > 1 ? ((priceChange / prices[0]) * 100).toFixed(1) : 0;

  const data = {
    labels: history.map(h => {
      const date = new Date(h.timestamp);
      return date.toLocaleDateString("en-IN", { 
        month: "short", 
        day: "numeric",
        hour: "2-digit"
      });
    }),
    datasets: [
      {
        label: "Price (₹)",
        data: prices,
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 8,
        pointBackgroundColor: "#3b82f6",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        borderWidth: 3,
      },
      {
        label: "Target Price",
        data: Array(history.length).fill(targetPrice),
        borderColor: "#10b981",
        borderDash: [8, 4],
        pointRadius: 0,
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        display: true,
        position: "top",
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 13,
            weight: "600"
          }
        }
      },
      tooltip: {
        backgroundColor: "#1f2937",
        titleColor: "#fff",
        bodyColor: "#fff",
        padding: 12,
        displayColors: false,
        callbacks: {
          label: function (context) {
            return `₹${context.parsed.y.toLocaleString()}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: "#f3f4f6",
        },
        ticks: {
          callback: function (value) {
            return "₹" + value.toLocaleString();
          },
          font: {
            size: 12
          }
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          font: {
            size: 11
          }
        }
      }
    },
  };

  return (
    <div className="chart-modal-overlay" onClick={onClose}>
      <div className="chart-card" onClick={(e) => e.stopPropagation()}>
        <button className="chart-close-btn" onClick={onClose}>✕</button>

        {/* Header */}
        <div className="chart-header">
          <h2>📊 Price History</h2>
          <p className="product-name-chart">{productName}</p>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon current">💰</div>
            <div className="stat-content">
              <span className="stat-label">Current</span>
              <span className="stat-value">₹{currentPrice.toLocaleString()}</span>
              {priceChange !== 0 && (
                <span className={`stat-change ${priceChange < 0 ? 'down' : 'up'}`}>
                  {priceChange < 0 ? '↓' : '↑'} {Math.abs(priceChangePercent)}%
                </span>
              )}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon lowest">📉</div>
            <div className="stat-content">
              <span className="stat-label">Lowest</span>
              <span className="stat-value">₹{lowestPrice.toLocaleString()}</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon highest">📈</div>
            <div className="stat-content">
              <span className="stat-label">Highest</span>
              <span className="stat-value">₹{highestPrice.toLocaleString()}</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon average">📊</div>
            <div className="stat-content">
              <span className="stat-label">Average</span>
              <span className="stat-value">₹{avgPrice.toFixed(0).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="chart-container">
          <Line data={data} options={options} />
        </div>

        {/* Footer Info */}
        <div className="chart-footer">
          <div className="tracking-info">
            <span className="tracking-badge">
              📍 Tracking {history.length} price point{history.length !== 1 ? "s" : ""}
            </span>
          </div>
          
          {currentPrice <= targetPrice && (
            <div className="deal-banner">
              🎉 <strong>Great Deal!</strong> Price is at or below your target!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PriceChart;