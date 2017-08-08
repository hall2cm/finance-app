var path = require("path");
var webpack = require("webpack");
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var ManifestRevisionPlugin = require("manifest-revision-webpack-plugin");
var TransferWebpackPlugin = require('transfer-webpack-plugin');

var rootAssetPath = "./app/static";

module.exports = {
  entry: {
    app_js: [
      rootAssetPath + "/js/app.js",
    ],
    main_css: [
      rootAssetPath + "/css/main.css"
    ],
    cognito_js: [
      rootAssetPath + "/js/auth.js"
    ],
    //foundation_js: [
      //"foundation-sites!./foundation-sites.config.js"
    //],
    foundation_css: [
      rootAssetPath + "/css/main.scss"
    ]

  },
  output: {
    path: "./app/build/public",
    publicPath: "http://localhost:2992/assets/",
    filename: "[name].[chunkhash].js",
    chuncFilename: "[id].[chunkhash].chunk"
  },
  resolve: {
    extensions: ["", ".js", ".css", ".scss"],
    alias: {
      foundation: 'foundation-sites/js/foundation.core'
    }
  },
  module: {
    loaders: [
      {
        test: /\.js$/i,
        exclude: /node_modules/,
        loader: "babel-loader",
        query: {
          presets: ['es2015']
        }
      },
      {
        test: /\.css$/i,
        loader: ExtractTextPlugin.extract("style-loader", "css-loader")
      },
      {
        test: /\.scss$/i,
        loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader')
      },
      {
        test: /\.(jpe?g|png|gif|svg([\?]?.*))$/i,
        loaders: [
          'file?context=' + rootAssetPath + '&name=img/[name].[hash].[ext]'
        ]
      },
      {
        test: /\.json$/,
        loader: 'json'
      },
      //{
        //test: /foundation\/js\//,
        //loader: 'imports?jQuery=jquery'
      //},
      {
        test: /(foundation\.core)/,
        loader: 'exports?foundation=jQuery.fn.foundation'
      },
      {
        test: /datatables\.net.*/,
        exclude: /\.png$/i,
        loader: 'imports?define=>false'
      }

    ]
  },
  plugins: [
    new ExtractTextPlugin("[name].[chunkhash].css"),
    new ManifestRevisionPlugin(path.join("build", "manifest.json"), {
      rootAssetPath: rootAssetPath,
      ignorePaths: ["/static"]
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": "jquery"
    }),
    //new TransferWebpackPlugin([
      //{ from: 'node_modules/datatables.net-zf/images', to: ''}
    //]),
    //new webpack.optimize.UglifyJsPlugin(),
    //new webpack.optimize.DedupePlugin(),
    //new webpack.DefinePlugin({
      //"process.env": {
        //NODE_ENV: '"production"'
      //}
    //}),
    new webpack.NoErrorsPlugin()
  ]
}
