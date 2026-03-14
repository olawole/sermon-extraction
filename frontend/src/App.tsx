import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import AppLayout from '@/components/Layout/AppLayout';
import JobSubmissionPage from '@/pages/JobSubmissionPage';
import JobDetailsPage from '@/pages/JobDetailsPage';

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1a3a6c', // Deep blue
          borderRadius: 8,
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        },
        components: {
          Button: {
            controlHeight: 40,
            fontWeight: 600,
          },
          Card: {
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
          },
          Layout: {
            headerBg: '#ffffff',
            bodyBg: '#f8fafc',
          }
        }
      }}
    >
      <BrowserRouter>
        <AppLayout>
          <Routes>
            <Route path="/" element={<JobSubmissionPage />} />
            <Route path="/jobs/:id" element={<JobDetailsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
