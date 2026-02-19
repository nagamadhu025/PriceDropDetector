import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});


// Automatically add Authorization header to every request
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (unauthorized) globally
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      
      console.log("Session expired. Please login again.");
      // Optional: redirect to login
      // window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default API;