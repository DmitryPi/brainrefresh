import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import { fileURLToPath, URL } from 'node:url';
import { resolve } from 'path';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx()],
  root: resolve(__dirname, '.'),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000
  },
  build: {
    outDir: resolve(__dirname, '../brainrefresh'),
    indexPath: 'templates',
    assetsDir: '',
    manifest: false,
    emptyOutDir: false,
    target: 'es2015',
    rollupOptions: {
      input: {
        app: resolve(__dirname, 'index.html'),  // TODO: specify public path dir
        main: resolve(__dirname, 'src/main.js'),
      },
      output: {
        // Функция определения директорий для статики
        assetFileNames: (assetInfo) => {
          let extType = assetInfo.name.split('.').at(-1);
          if (/png|jpe?g|svg|gif|tiff|bmp/i.test(extType)) {
            extType = 'images';
          } else if (/ico/i.test(extType)) {
            extType = 'images/favicons';  // will work if favicon in src/
          }
          return `static/${extType}/[name][extname]`;
        },
        chunkFileNames: 'static/js/[name].js',  // with hash: 'js/[name]-[hash].js
        entryFileNames: 'static/js/[name].js',
      },
    }
  }
})
