var TEST_CONFIG = {
  appName: 'whysarustest',
  appVersion: '1'
};

var STAGING_CONFIG = {
  appName: 'whysaurus',
  appVersion: 'c',
};

var PROD_CONFIG = {
  appName: 'whysaurus',
  appVersion: 'a',
};

var preprocessAppYaml = function(config) {
  return {
    src : 'app.yaml.stub' ,
    dest: 'app.yaml',
    options: { inline : true, context : config }
  };
};

module.exports = function(grunt) {
  // configure the tasks
  grunt.initConfig({
    clean: {
      main: {
        src: [ 'app.yaml' ],
      },
    },

    preprocess: {
      test: preprocessAppYaml(TEST_CONFIG),
      staging: preprocessAppYaml(STAGING_CONFIG),
      prod: preprocessAppYaml(PROD_CONFIG),
    },

    shell: {
      local: {
        command: 'dev_appserver.py --skip_sdk_update_check --host localhost --port 8081 --admin_host localhost .',
        options: {
          async: true,
        },
      },
    },
  });

  // load the tasks
  grunt.loadNpmTasks('grunt-autoprefixer');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-preprocess');
  grunt.loadNpmTasks('grunt-shell-spawn');

  // define the tasks
  grunt.registerTask('local', 'Builds and deploys to the TEST appengine environment.',
                        [ 'clean', 'preprocess:test', 'shell:local' ]);
                   
  grunt.registerTask('test', 'Builds and deploys to the TEST appengine environment.',
                        [ 'clean', 'preprocess:test' ]);
                        
  grunt.registerTask('staging', 'Builds and deploys to the STAGING appengine environment.',
                        [ 'clean', 'preprocess:staging']);
                        
  grunt.registerTask('prod', 'Builds and deploys to the PROD appengine environment.',
                        [ 'clean', 'preprocess:prod' ]);

};
