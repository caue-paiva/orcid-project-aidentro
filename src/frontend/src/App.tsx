import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import SignIn from "./pages/SignIn";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Dashboard from "./pages/Dashboard";
import DashboardSocial from "./pages/DashboardSocial";
import Search from "./pages/Search";
import Onboarding from "./pages/Onboarding";
import NotFound from "./pages/NotFound";
import AuthSuccess from "./pages/AuthSuccess";
import AuthError from "./pages/AuthError";
import OrcidTest from "./pages/OrcidTest";
import CitationTestDashboard from "./pages/CitationTestDashboard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/register" element={<Register />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/profile/:id" element={<Profile />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dashboard-social" element={<DashboardSocial />} />
          <Route path="/search" element={<Search />} />
          
          {/* Auth callback routes */}
          <Route path="/auth/success" element={<AuthSuccess />} />
          <Route path="/auth/error" element={<AuthError />} />
          
          {/* Test routes */}
          <Route path="/orcid-test" element={<OrcidTest />} />
          <Route path="/citation-test" element={<CitationTestDashboard />} />
          
          {/* Placeholder routes to avoid 404s */}
          <Route path="/about" element={<Home />} />
          <Route path="/researchers" element={<Home />} />
          <Route path="/membership" element={<Home />} />
          <Route path="/documentation" element={<Home />} />
          <Route path="/resources" element={<Home />} />
          <Route path="/news" element={<Home />} />
          
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
