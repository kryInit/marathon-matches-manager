module.exports = {
  mode: "development",

  entry: "./src/index.tsx",
  output: {
    path: `${__dirname}/../marathon_matches_manager/static`,
    filename: "bundle.js"
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader"
      }
    ]
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js", ".json"]
  },
  target: ["web", "es5"],
  devServer: {
    port: 3000,
    static: {
      directory: './src/'
    },
  }
};
