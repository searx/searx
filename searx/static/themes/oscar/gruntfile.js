module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        // compile *.ts files
        ts: {
            oscar : {
                src: ['./typescript/**/*.ts'],
                out: './js/oscar.js',
                module: 'amd', //or commonjs
                target: 'es5', //or es3
                options: {
                    comments: true //preserves comments in output.
                }
            }
        },
        uglify: {
            oscar: {
                options: {
                    banner: '/* ! themes/oscar/js/oscar.min.js | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n'
                },
                files: {
                    './js/oscar.min.js': ['./js/oscar.js']
                }
            }
        },
        jshint: {
            files: ['gruntfile.js'/*, 'js/searx_src/*.js'*/],
            options: {
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
                    paths: ["less/oscar"]
                    //banner: '/*! less/oscar/oscar.css | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n'
                },
                files: {"css/oscar.css": "less/oscar/oscar.less"}
            },
            production: {
                options: {
                    paths: ["less/oscar"],
                    //banner: '/*! less/oscar/oscar.css | <%= grunt.template.today("dd-mm-yyyy") %> | https://github.com/asciimoo/searx */\n',
                    cleancss: true
                },
                files: {"css/oscar.min.css": "less/oscar/oscar.less"}
            },
            bootstrap: {
                options: {
                    paths: ["less/bootstrap"],
                    cleancss: true
                },
                files: {"css/bootstrap.min.css": "less/bootstrap/bootstrap.less"}
            },
        },
        watch: {
            // watch scripts
            scripts: {
                files: ['./typescript/**/*.ts'],
                tasks: ['ts:oscar', 'uglify:oscar']
            },
            oscar_styles: {
                files: ['less/oscar/**/*.less'],
                tasks: ['less:development', 'less:production']
            },
            bootstrap_styles: {
                files: ['less/bootstrap/**/*.less'],
                tasks: ['less:bootstrap']
            }
        }
    });

    grunt.loadNpmTasks("grunt-ts");
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-less');

    grunt.registerTask('test', ['jshint']);
    grunt.registerTask('default', ['jshint', 'ts', 'uglify', 'less']);
    grunt.registerTask('scripts', ['jshint', 'ts', 'uglify']);
    grunt.registerTask('styles', ['less']);

};
