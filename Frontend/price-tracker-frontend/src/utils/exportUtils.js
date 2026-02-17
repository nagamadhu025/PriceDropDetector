// exportUtils.js

export const exportToCSV = (products, filename = "pricedrop-export") => {
  // CSV headers
  const headers = [
    "Product Name",
    "Current Price (₹)",
    "Target Price (₹)",
    "Discount (%)",
    "Savings (₹)",
    "Status",
    "Product URL",
    "Date Added"
  ];

  // Convert products to CSV rows
  const rows = products.map(product => {
    const discount = product.target_price > 0
      ? ((product.target_price - product.price) / product.target_price * 100).toFixed(1)
      : "0";
    
    const savings = Math.max(0, product.target_price - product.price).toFixed(0);
    
    return [
      `"${product.name.replace(/"/g, '""')}"`, // Escape quotes in product name
      product.price,
      product.target_price,
      discount,
      savings,
      product.subscribed ? "Active" : "Paused",
      product.url,
      new Date().toLocaleDateString()
    ];
  });

  // Combine headers and rows
  const csvContent = [
    headers.join(","),
    ...rows.map(row => row.join(","))
  ].join("\n");

  // Create blob and download
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}-${Date.now()}.csv`);
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const exportToJSON = (products, filename = "pricedrop-export") => {
  const data = products.map(product => ({
    name: product.name,
    currentPrice: product.price,
    targetPrice: product.target_price,
    url: product.url,
    image: product.image,
    status: product.subscribed ? "active" : "paused",
    exportDate: new Date().toISOString()
  }));

  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: "application/json" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}-${Date.now()}.json`);
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const shareProducts = (products) => {
  const deals = products.filter(p => p.price <= p.target_price);
  
  if (deals.length === 0) {
    return "No active deals to share right now!";
  }

  const text = deals.map(p => 
    `🎉 ${p.name}\n💰 Only ₹${p.price} (Target: ₹${p.target_price})\n🔗 ${p.url}`
  ).join("\n\n");

  return text;
};

export const shareToWhatsApp = (products) => {
  const text = shareProducts(products);
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(text)}`;
  window.open(whatsappUrl, "_blank");
};

export const copyToClipboard = (products) => {
  const text = shareProducts(products);
  navigator.clipboard.writeText(text).then(() => {
    alert("Deals copied to clipboard!");
  }).catch(err => {
    console.error("Failed to copy:", err);
  });
};