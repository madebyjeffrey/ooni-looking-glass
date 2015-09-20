module.exports = function(grunt) {
  require('load-grunt-tasks')(grunt);
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    cssmin: {
      incapp: {
        files: [{
          src: ['static/css/inc/bootstrap.min.css', 'static/css/flags.css', 'static/css/main.css'],
          dest: 'static/css/generated/incapp.min.css',
        }],
      },
    },

    concat: {
      inc: {
        src: ['static/js/inc/*.js'],
        dest: 'static/js/generated/libs.js',
        sourceMap: true
      }
    }
  });
  grunt.registerTask('default', ['concat:inc','cssmin:incapp']);


};
// vim: set ft=javascript tw=0 ts=2 sw=2 sts=2 fdm=marker fmr={{{,}}} et:
