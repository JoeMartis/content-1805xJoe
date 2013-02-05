(function (requirejs, require, define) {

  var baseURL;
 
  $('script').each(function (index, value) {
    var urlParse, path;

    urlParse = URI.parse(value.src);
        
    path = urlParse.path;
    if (!path.match(/\/js\/load\/matrixVector.js/g)) {
      return;
    }
    baseURL = path.replace(/\/js\/load\/matrixVector.js/g, '');
  });
    
  baseURL += '/js';
    
  //Loads the aliases of all our libraries and modules
  requirejs.config({
    baseUrl: baseURL,//'static/js',
    paths: {
      'jquery': 'vendor/jquery-1.7.2.min',
      'three': 'vendor/three.min',
      'webfonts': 'lib/webfonts',
      'tool': 'lib/tool',
      'utils': 'lib/utils',
      'color': 'lib/color',
      'vector2d': 'lib/vector2d',
      'component': 'lib/component',
      'radiobutton': 'lib/radiobutton',
      'checkbox': 'lib/checkbox',
      'slider': 'lib/slider',
      'vslider': 'lib/vslider',
      'button': 'lib/button',
      'text': 'lib/text',
      'label': 'lib/label',
      'font': 'lib/font',
      'graph': 'lib/graph',
      'minislider': 'lib/minislider',
      'radiobuttongroup': 'lib/radiobuttongroup',
      'dropdown': 'lib/dropdown',
      'textbox': 'lib/textbox',
      'richtext': 'lib/richtext',
      'rowarrow': 'lib/rowarrow'
    },
    shim: {
      'three': {
        deps: [],
        exports: 'THREE' //Attaches "THREE" to the window object
      }
    }    
  });

  //Load the library then call the application
  require(['lib/common'],function(){require(['app/matrixVector'])});

}(RequireJS.requirejs, RequireJS.require, RequireJS.define));