module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['src/js/*.js'],
        dest: 'js/searx.js'
      }
    },
    uglify: {
      options: {
        sourceMap: true,
        banner: '/*! oscar/searx.min.js | <%= grunt.template.today("dd-mm-yyyy") %> | <%= process.env.GIT_URL %>  */\n'
      },
      dist: {
        files: {
          'js/searx.min.js': ['<%= concat.dist.dest %>']
        }
      }
    },
    jshint: {
      files: ['gruntfile.js', 'js/searx_src/*.js'],
      options: {
        reporterOutput: "",
        // options here to override JSHint defaults
        globals: {
          jQuery: true,
          console: true,
          module: true,
          document: true
        }
      }
    },
    less: {
      development: {
        options: {
          paths: ["src/less/pointhi", "src/less/logicodev", "src/less/logicodev-dark"]
        },
        files: {
          "css/pointhi.css": "src/less/pointhi/oscar.less",
          "css/logicodev.css": "src/less/logicodev-dark/oscar.less",
          "css/logicodev-dark.css": "src/less/logicodev/oscar.less"
        }
      },
      production: {
        options: {
          paths: ["src/less/pointhi", "src/less/logicodev", "src/less/logicodev-dark"],
          plugins: [
            new (require('less-plugin-clean-css'))()
          ],
          sourceMap: true,
        },
        files: {
          "css/pointhi.min.css": "src/less/pointhi/oscar.less",
          "css/logicodev.min.css": "src/less/logicodev/oscar.less",
          "css/logicodev-dark.min.css": "src/less/logicodev-dark/oscar.less"
        }
      },
    },
    watch: {
        scripts: {
            files: ['<%= jshint.files %>'],
            tasks: ['jshint', 'concat', 'uglify']
        },
        oscar_styles: {
            files: ['src/less/pointhi/**/*.less'],
            tasks: ['less:development', 'less:production']
        },
        bootstrap_styles: {
            files: ['less/bootstrap/**/*.less'],
            tasks: ['less:bootstrap']
        }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-less');

  grunt.registerTask('test', ['jshint']);

  grunt.registerTask('default', ['jshint', 'concat', 'uglify', 'less']);

  grunt.registerTask('styles', ['less']);

};
