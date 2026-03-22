const path = require('path');

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      // Ignore source maps for node_modules to avoid issues with packages like zod
      webpackConfig.module.rules = webpackConfig.module.rules.map((rule) => {
        if (rule.enforce === 'pre' && rule.loader && rule.loader.includes('source-map-loader')) {
          return {
            ...rule,
            exclude: /node_modules/,
          };
        }
        return rule;
      });
      return webpackConfig;
    },
  },
};

