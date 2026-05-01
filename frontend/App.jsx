import React, { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import MainLayout from "./layout/MainLayout";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import Users from "./pages/Users";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Billing from "./pages/Billing";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import {
  clearStoredSession,
  getStoredSession,
  loginRequest,
  logoutRequest,
  meRequest,
  saveStoredSession,
  signupRequest,
} from "./api/client";
import "./styles.css";

const pages = [
  { id: "dashboard", path: "/dashboard", label: "Dashboard", component: Dashboard },
  { id: "analytics", path: "/analytics", label: "Analytics", component: Analytics },
  { id: "users", path: "/users", label: "Users", component: Users },
  { id: "reports", path: "/reports", label: "Reports", component: Reports },
  { id: "settings", path: "/settings", label: "Settings", component: Settings },
  { id: "billing", path: "/billing", label: "Billing", component: Billing },
  { id: "notifications", path: "/notifications", label: "Notifications", component: Notifications },
  { id: "profile", path: "/profile", label: "Profile", component: Profile },
];

function normalizeUser(user) {
  if (!user) {
    return null;
  }

  return {
    id: user.id,
    fullName: user.full_name ?? user.fullName ?? "Workspace User",
    email: user.email,
    role: user.role ?? "member",
  };
}

function AppRoutes({ authUser, authReady, onLogin, onSignup, onLogout }) {
  const location = useLocation();
  const routeKey = location.pathname;
  const activePage =
    pages.find((page) => page.path === location.pathname) ?? pages[0];

  if (!authReady) {
    return <div className="app-loading">Connecting to PulseStack backend...</div>;
  }

  if (location.pathname === "/" || location.pathname === "/login" || location.pathname === "/signup") {
    return (
      <Routes>
        <Route
          path="/"
          element={<div key={routeKey} className="route-transition"><Navigate to={authUser ? "/dashboard" : "/login"} replace /></div>}
        />
        <Route
          path="/login"
          element={
            <div key={routeKey} className="route-transition auth-route-transition">
              {authUser ? <Navigate to="/dashboard" replace /> : <Login onLogin={onLogin} />}
            </div>
          }
        />
        <Route
          path="/signup"
          element={
            <div key={routeKey} className="route-transition auth-route-transition">
              {authUser ? <Navigate to="/dashboard" replace /> : <Signup onSignup={onSignup} />}
            </div>
          }
        />
      </Routes>
    );
  }

  if (!authUser) {
    return <Navigate to="/login" replace />;
  }

  return (
    <MainLayout
      pages={pages}
      activePageId={activePage.id}
      pageTitle={activePage.label}
      authUser={authUser}
      onLogout={onLogout}
      routeKey={routeKey}
    >
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        {pages.map((page) => {
          const PageComponent = page.component;
          return <Route key={page.id} path={page.path} element={<PageComponent />} />;
        })}
      </Routes>
    </MainLayout>
  );
}

export default function App() {
  const [authUser, setAuthUser] = useState(null);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    const session = getStoredSession();
    if (!session?.token) {
      setAuthReady(true);
      return;
    }

    meRequest(session.token)
      .then((user) => {
        const normalizedSession = {
          token: session.token,
          user: normalizeUser(user),
        };
        saveStoredSession(normalizedSession);
        setAuthUser(normalizedSession);
      })
      .catch(() => {
        clearStoredSession();
        setAuthUser(null);
      })
      .finally(() => setAuthReady(true));
  }, []);

  async function handleLogin(credentials) {
    try {
      const session = await loginRequest(credentials);
      const normalizedSession = {
        ...session,
        user: normalizeUser(session.user),
      };
      saveStoredSession(normalizedSession);
      setAuthUser(normalizedSession);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.message || "Login failed.",
      };
    }
  }

  async function handleSignup(account) {
    try {
      const session = await signupRequest(account);
      const normalizedSession = {
        ...session,
        user: normalizeUser(session.user),
      };
      saveStoredSession(normalizedSession);
      setAuthUser(normalizedSession);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.message || "Signup failed.",
      };
    }
  }

  async function handleLogout() {
    if (authUser?.token) {
      try {
        await logoutRequest(authUser.token);
      } catch {
        // Frontend still clears local state even if backend logout fails.
      }
    }

    clearStoredSession();
    setAuthUser(null);
  }

  return (
    <BrowserRouter>
      <AppRoutes
        authUser={authUser?.user ?? null}
        authReady={authReady}
        onLogin={handleLogin}
        onSignup={handleSignup}
        onLogout={handleLogout}
      />
    </BrowserRouter>
  );
}
