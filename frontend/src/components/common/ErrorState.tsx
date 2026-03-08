import React from 'react';
import { Alert } from 'antd';

const ErrorState: React.FC<{ message?: string }> = ({ message = 'Something went wrong.' }) => (
  <Alert type="error" message={message} style={{ margin: 24 }} />
);

export default ErrorState;
