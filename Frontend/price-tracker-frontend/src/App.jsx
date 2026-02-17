import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import AddProduct from "./components/AddProduct";
import Login from "./Login/Login";   // 👈 add this

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />        {/* default page */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/add" element={<AddProduct />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
