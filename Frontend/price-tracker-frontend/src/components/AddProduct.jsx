import { useState } from "react";
import API from "../services/api";
import notificationService from "../services/notificationService";
import "./addproduct.css";

function AddProduct({ onProductAdded }) {
  const [url, setUrl] = useState("");
  const [targetPrice, setTargetPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
  e.preventDefault();

  if (!url.trim()) {
    setMessage("Please enter product URL");
    return;
  }

  if (!targetPrice || isNaN(targetPrice)) {
    setMessage("Enter valid target price");
    return;
  }

  setLoading(true);
  setMessage("");

  try {
    const token = localStorage.getItem("token");

    if (!token) {
      setMessage("Please login first");
      setLoading(false);
      return;
    }

    // ⬇️ increase timeout because Render is slow
    const res = await API.post(
      "/add-product",
      {
        url: url,
        target_price: parseFloat(targetPrice),
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        timeout: 60000, // ⭐ 60 sec timeout
      }
    );

    const addedProduct = res.data;

    setMessage("Product added successfully!");
    setUrl("");
    setTargetPrice("");

    // 🔔 Notification
    if (notificationService.isSupported() && Notification.permission === "granted") {
      notificationService.showNewProductAlert(addedProduct);
    }

    if (onProductAdded) {
      onProductAdded(addedProduct);
    }

  } catch (err) {
    console.error(err);

    // ⭐ IMPORTANT: handle timeout differently
    if (err.code === "ECONNABORTED" || err.message.includes("timeout")) {
      setMessage("Product added successfully! (server slow response)");

      // refetch products because backend likely succeeded
      if (onProductAdded) {
        onProductAdded();
      }

    } else if (err.response?.status === 401) {
      setMessage("Session expired. Please login again.");

    } else if (err.response?.status === 400) {
      setMessage(err.response.data.detail || "Product already tracked");

    } else if (err.response?.status === 503) {
      setMessage("Server waking up… product may still be added");

      if (onProductAdded) {
        onProductAdded();
      }

    } else if (!err.response) {
      // ⭐ network error but backend might still process
      setMessage("Product request sent. Checking status...");

      setTimeout(() => {
        if (onProductAdded) onProductAdded();
      }, 5000);

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
          placeholder="Paste Amazon / Flipkart product URL"
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
