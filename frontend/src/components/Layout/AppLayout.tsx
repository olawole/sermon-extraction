import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const { Header, Content } = Layout;

const StyledHeader = styled(Header)`
  display: flex;
  align-items: center;
  gap: 24px;
  background: #001529;
`;

const AppTitle = styled(Typography.Text)`
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
`;

const StyledContent = styled(Content)`
  padding: 24px;
  min-height: calc(100vh - 64px);
  background: #f0f2f5;
`;

interface Props {
  children: React.ReactNode;
}

const AppLayout: React.FC<Props> = ({ children }) => (
  <Layout style={{ minHeight: '100vh' }}>
    <StyledHeader>
      <AppTitle>
        <Link to="/" style={{ color: '#fff', textDecoration: 'none' }}>
          ✝ Sermon Extraction
        </Link>
      </AppTitle>
      <Menu
        theme="dark"
        mode="horizontal"
        selectable={false}
        items={[{ key: 'home', label: <Link to="/">Jobs</Link> }]}
        style={{ flex: 1, background: 'transparent', borderBottom: 'none' }}
      />
    </StyledHeader>
    <StyledContent>{children}</StyledContent>
  </Layout>
);

export default AppLayout;
