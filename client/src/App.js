import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';

// NEW: real CIA Wizard + Ops Credit components
import CIAWizard from './components/CIA/CIAWizard';
import CreditDisplay from './components/OpsCreditSystem/CreditDisplay';

// Theme definition
const theme = {
  colors: {
    primary: '#5B21B6', // Deep Purple (primary brand color)
    secondary: '#2563EB', // Electric Blue (secondary brand color)
    success: '#0D9488', // Teal (success and positive indicators)
    warning: '#F59E0B', // Amber (warnings and attention indicators)
    error: '#E11D48', // Ruby (errors and critical alerts)
    background: {
      dark: '#111827', // Rich dark background
      light: '#FFFFFF', // Clean white background
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#94A3B8',
    }
  },
  gradients: {
    primary: 'linear-gradient(135deg, #5B21B6 0%, #2563EB 100%)',
  },
  fonts: {
    primary: "'Inter', sans-serif",
    code: "'Roboto Mono', monospace",
  },
  borderRadius: '8px',
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
};

// Global styles
const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono:wght@400;500&display=swap');
  
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  body {
    font-family: ${props => props.theme.fonts.primary};
    background-color: ${props => props.theme.colors.background.dark};
    color: ${props => props.theme.colors.text.primary};
    line-height: 1.5;
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    margin-bottom: 1rem;
  }
`;

// Styled components
const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

const Header = styled.header`
  background: ${props => props.theme.gradients.primary};
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: ${props => props.theme.boxShadow};
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.75rem;
  }
`;

const UserMenu = styled.div`
  display: flex;
  align-items: center;
  
  button {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: ${props => props.theme.borderRadius};
    cursor: pointer;
    transition: background 0.3s ease;
    margin-right: 0.5rem; /* allow buttons to sit side-by-side */
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  }
`;

const MainLayout = styled.div`
  display: flex;
  flex: 1;
`;

const SideNav = styled.nav`
  width: 250px;
  background-color: rgba(0, 0, 0, 0.2);
  padding: 2rem 1rem;
`;

const NavSection = styled.div`
  margin-bottom: 2rem;
  
  h3 {
    color: ${props => props.theme.colors.text.secondary};
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
    padding: 0 0.75rem;
  }
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  padding: 0.75rem;
  color: ${props => props.theme.colors.text.primary};
  text-decoration: none;
  border-radius: ${props => props.theme.borderRadius};
  margin-bottom: 0.25rem;
  transition: background 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }
  
  &.active {
    background: rgba(255, 255, 255, 0.1);
    font-weight: 500;
  }
  
  svg {
    margin-right: 0.75rem;
  }
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
`;

const PlaceholderCard = styled.div`
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: ${props => props.theme.borderRadius};
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: ${props => props.theme.boxShadow};
`;

const GradientText = styled.span`
  background: ${props => props.theme.gradients.primary};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 600;
`;

const ProgressRing = styled.div`
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(
    ${props => props.theme.colors.primary} ${props => props.progress}%, 
    rgba(255, 255, 255, 0.1) 0%
  );
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2rem auto;
  
  &::before {
    content: '';
    position: absolute;
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: ${props => props.theme.colors.background.dark};
  }
  
  span {
    position: relative;
    font-size: 1.5rem;
    font-weight: 600;
    z-index: 1;
  }
`;

// Placeholder pages
const Dashboard = () => (
  <>
    <h1>Welcome to <GradientText>Project Waterfall</GradientText></h1>
    <p>Your marketing intelligence platform is being initialized.</p>
    
    <PlaceholderCard>
      <h2>Implementation Progress</h2>
      <ProgressRing progress={25}>
        <span>25%</span>
      </ProgressRing>
      <p>Phase 1: Foundation (in progress)</p>
    </PlaceholderCard>
    
    <PlaceholderCard>
      <h2>Getting Started</h2>
      <p>Project Waterfall is a comprehensive marketing intelligence platform designed to empower marketers, AI enthusiasts, and entrepreneurs with powerful tools for content creation, SEO optimization, and marketing strategy development.</p>
      <p>The platform integrates multiple data sources through a unified interface inspired by CleanMyMac's aesthetic.</p>
    </PlaceholderCard>
  </>
);

const ClarityBoard = () => (
  <>
    <h1><GradientText>Clarity Board</GradientText></h1>
    <p>A lightweight, free version of CIA that allows new users to experience the platform's capabilities without full commitment.</p>
    
    <PlaceholderCard>
      <h2>Coming Soon</h2>
      <p>The Clarity Board is scheduled for Phase 2 development.</p>
    </PlaceholderCard>
  </>
);

const CartwheelBundle = () => (
  <>
    <h1><GradientText>Cartwheel Bundle</GradientText></h1>
    <p>A collection of SEO and content generation tools that leverage the data from CIA to continuously produce optimized content across multiple platforms and formats.</p>
    
    <PlaceholderCard>
      <h2>Coming Soon</h2>
      <p>The Cartwheel Bundle is scheduled for Phase 3 development.</p>
    </PlaceholderCard>
  </>
);

// Main App component
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  // Google OAuth sign-in handler
  const signInWithGoogle = () => {
    const width = 500;
    const height = 600;
    const left = window.screenX + (window.outerWidth - width) / 2;
    const top = window.screenY + (window.outerHeight - height) / 2.5;
    const authWindow = window.open(
      '/api/auth/google',
      'GoogleLogin',
      `width=${width},height=${height},left=${left},top=${top}`
    );

    // Listener waits for message from OAuth popup
    const handleMessage = (event) => {
      if (!event.data?.token) return;
      // Persist token if desired (localStorage)
      localStorage.setItem('token', event.data.token);
      localStorage.setItem('refreshToken', event.data.refreshToken);
      setUser(event.data.user);
      setIsAuthenticated(true);
      window.removeEventListener('message', handleMessage);
      authWindow?.close();
    };

    window.addEventListener('message', handleMessage, false);
  };

  // Demo login handler – sets a fake user for local testing
  const demoLogin = () => {
    const demoUser = {
      id: 'demo-user-123',
      email: 'demo@waterfall.dev',
      firstName: 'Demo',
      lastName: 'User',
      fullName: 'Demo User',
      subscription: 'pro',
      role: 'user',
    };
    setUser(demoUser);
    setIsAuthenticated(true);
    // Persist in localStorage to mimic real login
    localStorage.setItem('token', 'demo-token');
    localStorage.setItem('refreshToken', 'demo-refresh-token');
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setIsAuthenticated(false);
    setUser(null);
  };
  
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Router>
        <AppContainer>
          <Header>
            <Logo>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="white" />
                <path d="M2 17L12 22L22 17" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M2 12L12 17L22 12" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Project Waterfall
            </Logo>
            <UserMenu>
              {isAuthenticated ? (
                <button onClick={logout}>Sign Out</button>
              ) : (
                <>
                  <button onClick={signInWithGoogle}>Sign in with Google</button>
                  <button onClick={demoLogin}>Demo Login</button>
                </>
              )}
            </UserMenu>
          </Header>
          
          <MainLayout>
            <SideNav>
              <NavSection>
                <h3>Core Components</h3>
                <NavLink to="/">Dashboard</NavLink>
                <NavLink to="/cia">CIA</NavLink>
                <NavLink to="/clarity-board">Clarity Board</NavLink>
                <NavLink to="/cartwheel">Cartwheel Bundle</NavLink>
                <NavLink to="/credits">Ops Credits</NavLink>
              </NavSection>
              
              <NavSection>
                <h3>Tools</h3>
                <NavLink to="/tools/seo">SEO Intelligence</NavLink>
                <NavLink to="/tools/content">Content Generator</NavLink>
                <NavLink to="/tools/social">Social Media</NavLink>
              </NavSection>
            </SideNav>
            
            <MainContent>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/cia" element={<CIAWizard />} />
                <Route path="/clarity-board" element={<ClarityBoard />} />
                <Route path="/cartwheel" element={<CartwheelBundle />} />
                <Route path="/credits" element={<CreditDisplay />} />
                <Route path="*" element={<h1>Page Not Found</h1>} />
              </Routes>
            </MainContent>
          </MainLayout>
        </AppContainer>
      </Router>
    </ThemeProvider>
  );
}

export default App;
