module.exports = function(grunt) {

  const path = require('path');

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    watch: {
      scripts: {
        files: ['<%= jshint.files %>', 'less/*.less'],
        tasks: ['jshint', 'concat', 'uglify', 'webfont', 'less:development', 'less:production']
      }
    },
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
        banner: '/*! simple/searx.min.js | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n',
        preserveComments: 'some',
        sourceMap: true
      },
      dist: {
        files: {
          'js/searx.min.js': ['<%= concat.dist.dest %>']
        }
      }
    },
    jshint: {
      files: ['js/searx_src/*.js'],
      options: {
        reporterOutput: "",
        proto: true,
        // options here to override JSHint defaults
        globals: {
          browser: true,
          jQuery: false,
          devel: true
        }
      }
    },
    less: {
      development: {
        options: {
          paths: ["less"],
          banner: '/*! searx | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n'
        },
        files: {
          "css/searx.css": "less/style.less",
          "css/searx-rtl.css": "less/style-rtl.less"
        }
      },
      production: {
        options: {
          paths: ["less"],
          plugins: [
            new (require('less-plugin-clean-css'))({
              advanced: true,
              compatibility: 'ie8'
            })
          ],
          banner: '/*! searx | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n'
        },
        files: {
          "css/searx.min.css": "less/style.less",
          "css/searx-rtl.min.css": "less/style-rtl.less"
        }
      },
    },
    webfont: {
      icons: {
        // src: 'node_modules/ionicons-npm/src/*.svg',
        src: [
          'node_modules/ionicons-npm/src/navicon-round.svg',
          'node_modules/ionicons-npm/src/search.svg',
          'node_modules/ionicons-npm/src/play.svg',
          'node_modules/ionicons-npm/src/link.svg',
          'node_modules/ionicons-npm/src/chevron-up.svg',
          'node_modules/ionicons-npm/src/chevron-left.svg',
          'node_modules/ionicons-npm/src/chevron-right.svg',
          'node_modules/ionicons-npm/src/arrow-down-a.svg',
          'node_modules/ionicons-npm/src/arrow-up-a.svg',
          'node_modules/ionicons-npm/src/arrow-swap.svg',
          'node_modules/ionicons-npm/src/telephone.svg',
          'node_modules/ionicons-npm/src/android-arrow-dropdown.svg',
          'node_modules/ionicons-npm/src/android-globe.svg',
          'node_modules/ionicons-npm/src/android-time.svg',
          'node_modules/ionicons-npm/src/location.svg',
          'node_modules/ionicons-npm/src/alert-circled.svg',
          'node_modules/ionicons-npm/src/android-alert.svg',
          'node_modules/ionicons-npm/src/ios-film-outline.svg',
          'node_modules/ionicons-npm/src/music-note.svg',
          'node_modules/ionicons-npm/src/ion-close-round.svg',
          'node_modules/ionicons-npm/src/android-more-vertical.svg',
          'magnet.svg'
        ],
        dest: 'fonts',
        destLess: 'less',
        options: {
          font: 'ion',
          hashes : true,
          syntax: 'bem',
          styles : 'font,icon',
          types : 'eot,woff2,woff,ttf,svg',
          order : 'eot,woff2,woff,ttf,svg',
          stylesheets : ['css', 'less'],
          relativeFontPath : '../fonts/',
          autoHint : false,
          normalize : false,
          // ligatures : true,
          optimize : true,
          // fontHeight : 400,
          rename : function(name) {
            basename = path.basename(name);
            if (basename === 'android-alert.svg') {
              return 'error.svg';
            }
            if (basename === 'alert-circled.svg') {
              return 'warning.svg';
            }
            if (basename === 'ion-close-round.svg') {
              return 'close.svg';
            }
            return basename.replace(/(ios|md|android)-/i, '');
          },
          templateOptions: {
            baseClass: 'ion-icon',
            classPrefix: 'ion-'
          }
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-webfont');

  grunt.registerTask('test', ['jshint']);

  grunt.registerTask('default', ['jshint', 'concat', 'uglify', 'less:development', 'less:production']);
};
