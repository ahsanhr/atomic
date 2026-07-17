// main.jsx — React application entry point
//
// responsibilities:
//   - locate the root HTML element
//   - mount the React application
//   - load global styles
//   - provide any top-level router or context wrappers

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
