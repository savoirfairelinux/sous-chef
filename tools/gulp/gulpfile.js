'use strict';

// Load Plugins
// ==========================================
const gulp = require('gulp');
const bytediff = require('gulp-bytediff');
const minifycss = require('gulp-clean-css');
const rename = require('gulp-rename');
const sass = require('gulp-sass');
const autoprefixer = require('gulp-autoprefixer');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
const imagemin = require('gulp-imagemin');
const cache = require('gulp-cache');
const debug = require('gulp-debug');
const validate = require('gulp-jsvalidate');

// Paths
// ==========================================
// - Source path folders
const SRC_SCSS = '../../src/frontend/scss';
const SRC_JS = '../../src/frontend/js';
const SRC_IMG = '../../src/frontend/images';

// - Source paths
// Add any additional vendor or site files added to the appropriate property below.
const sources = {

  js: {
    scripts: {
      vendor: [
        'node_modules/jquery/dist/jquery.js',
        'node_modules/jquery-tablesort/jquery-tablesort.js',
        'node_modules/jquery.formset/src/jquery.formset.js',
        'node_modules/semantic-ui-css/semantic.js',
        'node_modules/semantic-ui-calendar/dist/calendar.js',
        'node_modules/dateformat/lib/dateformat.js',
      ],
      site: [
        `${SRC_JS}/global.js`,
        `${SRC_JS}/delivery.js`,
        `${SRC_JS}/member.js`,
        `${SRC_JS}/order.js`,
        `${SRC_JS}/billing.js`,
        `${SRC_JS}/page.js`,
        `${SRC_JS}/note.js`,
      ]
    },
    leaflet: {
      vendor: [
        'node_modules/leaflet-routing-machine/dist/leaflet-routing-machine.js',
        'node_modules/leaflet-control-geocoder/dist/Control.Geocoder.js',
        'node_modules/leaflet.awesome-markers/dist/leaflet.awesome-markers.js',
        'node_modules/leaflet.icon.glyph/Leaflet.Icon.Glyph.js',
        'node_modules/sortablejs/Sortable.js',
      ],
      site: [
        `${SRC_JS}/custom-leaflet.js`,
      ]
    },
    multiDatesPicker: {
      vendor: [
        'node_modules/jquery-ui-multi-date-picker/dist/jquery-ui.multidatespicker.js',
      ],
      site: [
        `${SRC_JS}/multidatespicker.js`,
      ]
    }
  },

  css: {
    vendor: [
      'node_modules/semantic-ui-css/semantic.css',
      'node_modules/semantic-ui-calendar/dist/calendar.css',
      'node_modules/leaflet-routing-machine/dist/leaflet-routing-machine.css',
      'node_modules/leaflet-control-geocoder/dist/Control.Geocoder.css',
      'node_modules/leaflet.awesome-markers/dist/leaflet.awesome-markers.css',
    ],
    site: [
      `${SRC_SCSS}/main.scss`,
    ]
  },

  img: {
    vendor: [
      'node_modules/semantic-ui-css/themes/default/assets/images/*.{png,svg}',
      'node_modules/leaflet-routing-machine/dist/*.{png,svg}',
      'node_modules/leaflet-control-geocoder/dist/images/*',
      'node_modules/leaflet.awesome-markers/dist/images/*',
      'node_modules/leaflet.icon.glyph/*.{png,svg}',
    ],
    site: [
      `${SRC_IMG}/**/*`,
    ]
  },

  fonts: {
    vendor: [
      'node_modules/semantic-ui-css/themes/default/assets/fonts/*',
    ]
  }
};

// - Destination path folders
const destinations = {
  css: '../../src/sous_chef/static/css',
  js: '../../src/sous_chef/static/js',
  img: '../../src/sous_chef/static/images',
  fonts: '../../src/sous_chef/static/fonts'
};

// Tasks
// ==========================================

gulp.task('styles', () =>
  gulp.src([].concat(sources.css.vendor).concat(sources.css.site))
    .pipe(sass({ style: 'expanded', errLogToConsole: true }))
    .pipe(autoprefixer({
      browsers: ['last 2 version', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4'],
      cascade: false
    }))
    .pipe(concat('main.css'))
    .pipe(bytediff.start())
    .pipe(gulp.dest('/tmp/css'))
    .pipe(rename({ suffix: '.min' }))
    .pipe(minifycss())
    .pipe(bytediff.stop(bytediffFormatter))
    .pipe(gulp.dest(destinations.css))
);

gulp.task('scripts', () =>
  gulp.src([].concat(sources.js.scripts.vendor).concat(sources.js.scripts.site))
    .pipe(concat('sous-chef.js'))
    .pipe(gulp.dest(destinations.js))
    .pipe(bytediff.start())
    .pipe(uglify())
    .pipe(bytediff.stop(bytediffFormatter))
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(destinations.js))
);

gulp.task('scripts-leaflet', () =>
  gulp.src([].concat(sources.js.leaflet.vendor).concat(sources.js.leaflet.site))
    .pipe(concat('leaflet.js'))
    .pipe(gulp.dest(destinations.js))
    .pipe(bytediff.start())
    .pipe(uglify())
    .pipe(bytediff.stop(bytediffFormatter))
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(destinations.js))
);

gulp.task('scripts-multidatespicker', () =>
  gulp.src([].concat(sources.js.multiDatesPicker.vendor).concat(sources.js.multiDatesPicker.site))
    .pipe(concat('multidatespicker.js'))
    .pipe(gulp.dest(destinations.js))
    .pipe(bytediff.start())
    .pipe(uglify())
    .pipe(bytediff.stop(bytediffFormatter))
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(destinations.js))
);

gulp.task('images', () =>
  gulp.src([].concat(sources.img.vendor).concat(sources.img.site))
    .pipe(cache(imagemin({
      optimizationLevel: 3,
      progressive: true,
      interlaced: true
    })))
    .pipe(gulp.dest(destinations.img))
);

gulp.task('fonts', () =>
  gulp.src([].concat(sources.fonts.vendor))
    .pipe(gulp.dest(destinations.fonts))
);

gulp.task('default', () => {
  gulp.start('styles', 'scripts-multidatespicker', 'scripts-leaflet', 'scripts',
  'images', 'fonts');
});

gulp.task('watch', ['default'], () => {
  gulp.watch(`${SRC_SCSS}/**/*.scss`, ['styles']);
  gulp.watch(`${SRC_JS}/**/*.js`, ['scripts-multidatespicker', 'scripts-leaflet', 'scripts']);
  gulp.watch(`${SRC_IMG}/**/*`, ['images']);
});

gulp.task('validate', () =>
  gulp.src([]
    .concat(sources.js.scripts.site)
    .concat(sources.js.leaflet.site)
    .concat(sources.js.multiDatesPicker.site)
  )
  .pipe(debug())
  .pipe(validate())
  .on('error', onError)
);


// Log errors on JS validation problems.
function onError(error) {
 console.log(error.message);

 if (error.plugin === 'gulp-jsvalidate') {
   console.log('In file: ' + error.fileName);
 }

 process.exit(1);
};

// Tell us how much our files have been compressed after minification.
function bytediffFormatter(data) {
  return `${data.fileName} went from ${(data.startSize / 1000).toFixed(2)} ` +
  `kB to ${(data.endSize / 1000).toFixed(2)} kB and is ` +
  `${formatPercent(1 - data.percent, 2)}% ` +
  `${(data.savings > 0) ? 'smaller' : 'larger'}.`;
};

function formatPercent(num, precision) {
  return (num * 100).toFixed(precision);
};
