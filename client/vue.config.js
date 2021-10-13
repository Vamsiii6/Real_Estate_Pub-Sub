var path = require('path')
module.exports = {
  devServer: {
    port: 8080,
  },
  configureWebpack: {
    resolve: {
      alias: {
        src: path.resolve(__dirname, 'src'),
        stlyes: path.resolve(__dirname, 'src/styles'),
        pages: path.resolve(__dirname, 'src/pages'),
        components: path.resolve(__dirname, 'src/components'),
        assets: path.resolve(__dirname, 'src/assets'),
        plugins: path.resolve(__dirname, 'src/plugins'),
        mixins: path.resolve(__dirname, 'src/mixins'),
      },
    },
  },
}
