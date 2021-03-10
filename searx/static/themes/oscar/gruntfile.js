module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['js/searx_src/*.js'],
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
          paths: ["less/pointhi", "less/logicodev", "less/logicodev-dark", "less/bootstrap"]
        },
        files: {
          "css/pointhi.css": "less/pointhi/oscar.less",
          "css/logicodev.css": "less/logicodev-dark/oscar.less",
          "css/logicodev-dark.css": "less/logicodev/oscar.less"
        }
      },
      production: {
        options: {
          paths: ["less/pointhi", "less/logicodev", "less/logicodev-dark", "less/bootstrap"],
          plugins: [
            new (require('less-plugin-clean-css'))()
          ],
          sourceMap: true,
        },
        files: {
          "css/pointhi.min.css": "less/pointhi/oscar.less",
          "css/logicodev.min.css": "less/logicodev/oscar.less",
          "css/logicodev-dark.min.css": "less/logicodev-dark/oscar.less"
        }
      },
    },
    watch: {
        scripts: {
            files: ['<%= jshint.files %>'],
            tasks: ['jshint', 'concat', 'uglify']
        },
        oscar_styles: {
            files: ['less/pointhi/**/*.less'],
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
