import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from '@/components/Layout/AppLayout';
import JobSubmissionPage from '@/pages/JobSubmissionPage';
import JobDetailsPage from '@/pages/JobDetailsPage';

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<JobSubmissionPage />} />
          <Route path="/jobs/:id" element={<JobDetailsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
