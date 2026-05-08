import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: './',
  plugins: [vue()],
  build: {
    outDir: 'dist',
    minify: false,
    cssMinify: false,
    target: 'es2018',
    sourcemap: false,
  }
})
