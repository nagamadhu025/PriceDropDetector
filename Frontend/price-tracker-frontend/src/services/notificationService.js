class NotificationService {
  constructor() {
    this.permission = typeof Notification !== "undefined" 
      ? Notification.permission 
      : "denied";
  }

  async requestPermission() {
    if (!this.isSupported()) return false;
    if (this.permission === "granted") return true;
    if (this.permission !== "denied") {
      const permission = await Notification.requestPermission();
      this.permission = permission;
      return permission === "granted";
    }
    return false;
  }

  showNotification(title, options = {}) {
    if (this.permission !== "granted") return;
    const notification = new Notification(title, {
      icon: options.icon || "/logo.png",
      body: options.body || "",
      tag: options.tag || "pricedrop",
      requireInteraction: options.requireInteraction || false,
      ...options,
    });
    notification.onclick = () => {
      window.focus();
      if (options.onClick) options.onClick();
      notification.close();
    };
    return notification;
  }

  showPriceDropAlert(product) {
    return this.showNotification("🎉 Price Drop Alert!", {
      body: `${product.name} is now ₹${product.price}`,
      icon: product.image || "/logo.png",
      tag: `product-${product.id}`,
      requireInteraction: true,
      onClick: () => window.open(product.url, "_blank"),
    });
  }

  isSupported() {
    return typeof window !== "undefined" && "Notification" in window;
  }

  getPermission() {
    return this.permission;
  }
}

const notificationService = new NotificationService();
export default notificationService;