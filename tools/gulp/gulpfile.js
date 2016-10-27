'use strict';

// http://stackoverflow.com/a/32940141
require('es6-promise').polyfill();

// Load Plugins
// ==========================================
var gulp = require('gulp');
var browsersync = require('browser-sync').create();
var minifycss = require('gulp-minify-css');
var rename = require('gulp-rename');
var sass = require('gulp-sass');
var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var imagemin = require('gulp-imagemin');
var cache = require('gulp-cache');
var debug = require('gulp-debug');
var validate = require('gulp-jsvalidate');

// Paths
// ==========================================
// - Source paths
var SRC_SCSS = '../../src/frontend/scss';
var SRC_JS = '../../src/frontend/js';
var SRC_IMG = '../../src/frontend/images';

// - Destination paths
// We use tmp destinations to avoid creating transitionary files in our work dir.
var DST_TMP_CSS = '/tmp/css';
var DST_TMP_CSS_NG = '/tmp/css-ng';
var DST_TMP_JS = '/tmp/js';
var DST_CSS = '../../src/sous-chef/static/css';
var DST_JS = '../../src/sous-chef/static/js';
var DST_IMG = '../../src/sous-chef/static/images';

// Tasks
// ==========================================

gulp.task('styles', function() {
    return gulp.src(SRC_SCSS + '/main.scss')
        .pipe(sass({ style: 'expanded', errLogToConsole: true }))
        .pipe(autoprefixer({
            browsers: ['last 2 version', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4'],
            cascade: false
        }))
        .pipe(gulp.dest(DST_TMP_CSS))
        .pipe(rename({ suffix: '.min' }))
        .pipe(minifycss())
        .pipe(gulp.dest(DST_CSS));
});

gulp.task('scss-watch', ['styles'], browsersync.reload);

gulp.task('scripts', function() {
    return gulp.src([
        SRC_JS + '/vendor/jquery/**/*.js',
        SRC_JS + '/vendor/calendar/**/*.js',
        SRC_JS + '/vendor/multidatespicker/*.js',
        SRC_JS + '/global.js',
        SRC_JS + '/delivery.js',
        SRC_JS + '/member.js',
        SRC_JS + '/order.js',
        SRC_JS + '/billing.js',
        SRC_JS + '/page.js',
    ])
        .pipe(concat('sous-chef.js'))
        .pipe(gulp.dest(DST_JS))
        .pipe(uglify())
        .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest(DST_JS));
});

gulp.task('scripts-leaflet', function() {
    return gulp.src([
        SRC_JS + '/vendor/leaflet-routing/**/*.js',
        SRC_JS + '/vendor/leaflet-geocoder/**/*.js',
        SRC_JS + '/vendor/leaflet-awesome-markers/**/*.js',
        SRC_JS + '/vendor/leaflet-icon-glyph/**/*.js',
        SRC_JS + '/vendor/sortable/**/*.js',
        SRC_JS + '/custom-leaflet.js',
    ])
        .pipe(concat('leaflet.js'))
        .pipe(gulp.dest(DST_JS))
        .pipe(uglify())
        .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest(DST_JS));
});

gulp.task('js-watch', ['scripts-leaflet', 'scripts'], browsersync.reload);

gulp.task('images', function() {
    return gulp.src([SRC_IMG + '/**/*'])
        .pipe(cache(imagemin({
            optimizationLevel: 3,
            progressive: true,
            interlaced: true
        })))
        .pipe(gulp.dest(DST_IMG));
});

gulp.task('images-watch', ['images'], browsersync.reload);

gulp.task('default', function() {
    gulp.start('styles', 'scripts-leaflet', 'scripts', 'images');
});

gulp.task('watch', ['default'], function() {
    browsersync.init({
        proxy: "localhost"
    });

    gulp.watch(SRC_SCSS + '/**/*.scss', ['scss-watch']);
    gulp.watch(SRC_JS + '/**/*.js', ['js-watch']);
    gulp.watch(SRC_IMG + '/**/*', ['images-watch']);
});

gulp.task('validate', function () {
   return gulp.src([
        SRC_JS + '/delivery.js',
        SRC_JS + '/member.js',
        SRC_JS + '/order.js',
        SRC_JS + '/page.js',
        SRC_JS + '/global.js',
    ])
        .pipe(debug())
        .pipe(validate())
        .on('error', onError);
});

function onError(error) {
   console.log(error.message);

   if (error.plugin === 'gulp-jsvalidate') {
       console.log('In file: ' + error.fileName);
   }

   process.exit(1);
}
