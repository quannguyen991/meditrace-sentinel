import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig} from 'vite';
import {cauHinhViteDev} from './may-chu/chan-tep-dev';

export default defineConfig(() => {
  // Không dùng allowedHosts: true (mở cho mọi Host). Tên miền đường hầm đặt qua MEDITRACE_ALLOWED_HOSTS.
  const {allowedHosts, fs} = cauHinhViteDev(__dirname, process.env);
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      ...(allowedHosts ? {allowedHosts} : {}),
      fs,
      host: process.env.HOST || '127.0.0.1',
      hmr: process.env.DISABLE_HMR !== 'true',
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
  };
});
