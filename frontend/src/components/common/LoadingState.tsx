import React from 'react';
import { Spin } from 'antd';
import styled from 'styled-components';

const Center = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 48px;
`;

const LoadingState: React.FC<{ tip?: string }> = ({ tip = 'Loading...' }) => (
  <Center>
    <Spin tip={tip} size="large" />
  </Center>
);

export default LoadingState;
