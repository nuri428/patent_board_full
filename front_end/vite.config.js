import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8005';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            if (proxyRes.headers['location']) {
              proxyRes.headers['location'] = proxyRes.headers['location'].replace('http://backend:5000', '');
              proxyRes.headers['location'] = proxyRes.headers['location'].replace('https://backend:5000', '');
            }
          });
        },
      },
    },
  },
})
