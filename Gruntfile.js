module.exports = function(grunt) {
  require('load-grunt-tasks')(grunt);
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    concat: {
      dist: {
        src: ['static/js/concat/*.js'],
        dest: 'static/js/concatlibs.min.js'
      }
    }
  });
  grunt.registerTask('default', ['concat:dist']);


};
// vim: set ft=javascript tw=0 ts=2 sw=2 sts=2 fdm=marker fmr={{{,}}} et:
