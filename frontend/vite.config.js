import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5001',
    },
    watch: {
      ignored: [
        '**/backend/**',
        '**/problems/**',
        '**/node_modules/**',
        '**/.git/**',
      ],
      usePolling: false,
      stabilityThreshold: 300,
    },
  },
  optimizeDeps: {
    include: ['@monaco-editor/react'],
  },
})
