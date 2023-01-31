const { defineConfig } = require('@vue/cli-service')
const path = require("path")

module.exports = defineConfig({
  publicPath: process.env.VUE_APP_STATIC_URL,
  outputDir: path.resolve(__dirname, "../static", "questions"),
  indexPath: path.resolve(__dirname, "../templates/", "questions", "index.html"),
  devServer: {
    proxy: "http://localhost:8000"
  }
})
