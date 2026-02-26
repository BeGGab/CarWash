import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { 
    allowedHosts: [
      'https://4987b979b82824b0-5-167-124-3.serveousercontent.com',
      '.serveousercontent.com'
    ],
    host: true, 
    port: 3000, 
    proxy: { 
      '/api/v1': { 
        target: 'http://localhost:8000', 
        changeOrigin: true,
        secure: false
        } 
    } 
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
