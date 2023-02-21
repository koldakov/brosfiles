class Utils {
  static easySelect(el, everything = false) {
    el = el.trim();

    if (everything) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  static easyOn(type, el, listener, everything = false){
    if (everything) {
      this.easySelect(el, everything).forEach(e => e.addEventListener(type, listener))
    } else {
      this.easySelect(el, everything).addEventListener(type, listener)
    }
  }

  static onScroll(el, listener) {
    el.addEventListener('scroll', listener);
  }
}


// I prefer old style
(function() {
  'use strict';

  if (Utils.easySelect('.toggle-sidebar-btn')) {
    Utils.easyOn('click', '.toggle-sidebar-btn', function(e) {
      Utils.easySelect('body').classList.toggle('toggle-sidebar');
    })
  }

  if (Utils.easySelect('.search-bar-toggle')) {
    Utils.easyOn('click', '.search-bar-toggle', function(e) {
      Utils.easySelect('.search-bar').classList.toggle('search-bar-show');
    })
  }
})();
