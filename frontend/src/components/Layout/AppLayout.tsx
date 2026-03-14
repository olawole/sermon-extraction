import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const { Header, Content } = Layout;

const StyledHeader = styled(Header)`
  display: flex;
  align-items: center;
  gap: 32px;
  background: #ffffff;
  padding: 0 40px;
  border-bottom: 1px solid #f1f5f9;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
  height: 72px;
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
`;

const AppLogo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  
  &:hover {
    opacity: 0.8;
  }
`;

const AppTitle = styled(Typography.Title)`
  margin: 0 !important;
  font-size: 20px !important;
  font-weight: 800 !important;
  background: linear-gradient(to right, #1a3a6c, #2563eb);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.025em;
`;

const StyledContent = styled(Content)`
  padding: 0;
  min-height: calc(100vh - 72px);
  background: transparent;
`;

interface Props {
  children: React.ReactNode;
}

const AppLayout: React.FC<Props> = ({ children }) => {
  const location = useLocation();
  const selectedKey = location.pathname === '/' ? 'home' : '';

  return (
    <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
      <StyledHeader>
        <Link to="/" style={{ textDecoration: 'none' }}>
          <AppLogo>
            <span style={{ fontSize: '24px' }}>✝</span>
            <AppTitle level={4}>SermonExtraction</AppTitle>
          </AppLogo>
        </Link>
        <Menu
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={[
            { 
              key: 'home', 
              label: <Link to="/" style={{ fontWeight: 500 }}>Dashboard</Link> 
            }
          ]}
          style={{ 
            flex: 1, 
            background: 'transparent', 
            borderBottom: 'none',
            fontSize: '15px'
          }}
        />
      </StyledHeader>
      <StyledContent>{children}</StyledContent>
    </Layout>
  );
};

export default AppLayout;
