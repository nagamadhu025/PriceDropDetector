import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./Login.css";

export default function Login() {
  const [isSignup, setIsSignup] = useState(false);
  const [showOTPScreen, setShowOTPScreen] = useState(false);  // ⭐ NEW
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");  // ⭐ NEW

  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

const handleLogin = async (e) => {
  e.preventDefault();
  setMsg("");
  setLoading(true);

  try {
    // ⭐ Clear old user data first
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    const res = await API.post("/login", { email, password });
    
    localStorage.setItem("token", res.data.access_token);
    localStorage.setItem("user", JSON.stringify(res.data.user));
    
    setEmail("");
    setPassword("");
    
    navigate("/dashboard");
    } catch (err) {
      if (err.response?.status === 403) {
        setMsg("⚠️ Please verify your email first. Check your inbox!");
      } else {
        setMsg(err.response?.data?.detail || "Login failed");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setMsg("");
    setLoading(true);

    try {
      const res = await API.post("/register", { name, email, password });
      
      setMsg("✅ " + res.data.message);
      setShowOTPScreen(true);  // ⭐ Show OTP input screen
      
      
    } catch (err) {
      setMsg(err.response?.data?.detail || "Register failed");
    } finally {
      setLoading(false);
    }
  };

 const handleVerifyOTP = async (e) => {
  e.preventDefault();
  setMsg("");
  setLoading(true);

  try {
    // Step 1: Verify OTP
    await API.post("/verify-otp", { email, otp_code: otp });
    
    setMsg("✅ Email verified! Logging you in...");

    // Step 2: Auto login with same credentials
    const loginRes = await API.post("/login", { email, password });

    // Step 3: Clear old data, store NEW user
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.setItem("token", loginRes.data.access_token);
    localStorage.setItem("user", JSON.stringify(loginRes.data.user));

    // Step 4: Go to dashboard
    setTimeout(() => {
      navigate("/dashboard");
    }, 1500);
      
    } catch (err) {
      setMsg("❌ " + (err.response?.data?.detail || "Invalid OTP"));
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setMsg("");
    setLoading(true);

    try {
      const res = await API.post("/resend-otp", { email });
      setMsg("✅ " + res.data.message);
    } catch (err) {
      setMsg("❌ Failed to resend OTP");
    } finally {
      setLoading(false);
    }
  };

  // ⭐ OTP Verification Screen
  if (showOTPScreen) {
    return (
      <div className="login-page">
        <div className="login-box">
          <h2>📧 Verify Your Email</h2>
          <p className="otp-instruction">
            We've sent a 6-digit code to <strong>{email}</strong>
          </p>

          <form onSubmit={handleVerifyOTP}>
            <div className="input-group">
              <input
                type="text"
                required
                maxLength="6"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                placeholder="Enter 6-digit code"
                className="otp-input"
              />
              <label>Verification Code</label>
            </div>

            <button type="submit" disabled={loading || otp.length !== 6}>
              {loading ? "Verifying..." : "Verify Email"}
            </button>
          </form>

          <p className="resend-text">
            Didn't receive the code?{" "}
            <span 
              className="resend-link" 
              onClick={handleResendOTP}
            >
              Resend OTP
            </span>
          </p>

          <p className="toggle-text" onClick={() => setShowOTPScreen(false)}>
            ← Back to registration
          </p>

          {msg && <p className={msg.includes("✅") ? "success-message message" : "error-message message"}>{msg}</p>}
        </div>
      </div>
    );
  }

  // ⭐ Regular Login/Register Screen
  return (
    <div className="login-page">
      <div className="login-box">
        <h2>{isSignup ? "Create Account" : "Welcome Back to PriceDrop"}</h2>

        <form onSubmit={isSignup ? handleRegister : handleLogin}>
          {isSignup && (
            <div className="input-group">
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <label>Name</label>
            </div>
          )}

          <div className="input-group">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <label>Email</label>
          </div>

          <div className="input-group password-group">
            <input
              type={showPass ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <label>Password</label>

            <span
              className="toggle-pass"
              onClick={() => setShowPass(!showPass)}
            >
              {showPass ? "Hide" : "Show"}
            </span>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Please wait..." : isSignup ? "Register" : "Login"}
          </button>
        </form>

        <p className="toggle-text" onClick={() => {
          setIsSignup(!isSignup);
          setMsg("");
        }}>
          {isSignup ? "Already have an account? Login" : "New here? Create account"}
        </p>

        {msg && <p className={msg.includes("✅") ? "success-message message" : "error-message message"}>{msg}</p>}
      </div>
    </div>
  );
}