import React from 'react';
import { Empty } from 'antd';
import styled from 'styled-components';

const Center = styled.div`
  padding: 48px;
  text-align: center;
`;

const EmptyState: React.FC<{ description?: string }> = ({ description }) => (
  <Center>
    <Empty description={description} />
  </Center>
);

export default EmptyState;
