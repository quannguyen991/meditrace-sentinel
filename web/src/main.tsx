import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import Goc from './Goc.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Goc />
  </StrictMode>,
);
