
window.goToAnchor = function (anchorname) {
    var target;
  target = $('[name=' + anchorname +']');
  if (target.length) {
    $('html,body').animate({
      scrollTop: target.offset().top - ($('nav').height()+18)
    }, 1000);
    return false;
  }
}
