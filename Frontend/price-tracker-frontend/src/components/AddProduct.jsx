import { useState } from "react";
import API from "../services/api";
import "./addproduct.css";

function AddProduct({ onProductAdded }) {
  const [url, setUrl] = useState("");
  const [targetPrice, setTargetPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      // Get token from localStorage
      const token = localStorage.getItem("token");

      if (!token) {
        setMessage("Please login first");
        setLoading(false);
        return;
      }

      // Send data in request BODY (not params), with Authorization header
      await API.post(
        "/add-product",
        {
          url: url,
          target_price: parseFloat(targetPrice), // Convert to number
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMessage("Product added successfully!");
      setUrl("");
      setTargetPrice("");

      // Refresh product list
      if (onProductAdded) {
        onProductAdded();
      }
    } catch (err) {
      console.error(err);
      
      // Better error handling
      if (err.response?.status === 401) {
        setMessage("Session expired. Please login again.");
        // Optional: redirect to login
        // window.location.href = '/login';
      } else if (err.response?.status === 400) {
        setMessage(err.response.data.detail || "Product already tracked");
      } else if (err.response?.status === 503) {
        setMessage("Could not fetch product details. Try again later.");
      } else {
        setMessage(err.response?.data?.detail || "Failed to add product");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-product">
      <h3>Add New Product</h3>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Amazon product URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />

        <input
          type="number"
          step="0.01"
          placeholder="Target price"
          value={targetPrice}
          onChange={(e) => setTargetPrice(e.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner"></span>
              Adding...
            </>
          ) : (
            "Track Product"
          )}
        </button>
      </form>

      {message && (
        <p className={message.includes("success") ? "success" : "error"}>
          {message}
        </p>
      )}
    </div>
  );
}

export default AddProduct;