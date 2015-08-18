$(document).ready(function() {
  $(window).scroll(function() {
    if($(this).scrollTop() >= 400) {
      $('#scrolltop').fadeIn();
      $('#scrollbottom').fadeIn();
    } else {
      $('#scrolltop').fadeOut();
      $('#scrollbottom').fadeOut();
    }
  });
});

$(document).ready(function(){
   $('#scrolltop').hover(function() {
      $(this).stop().fadeTo('slow',1);
   },
   function() {
      $(this).stop().fadeTo('slow',0.5);
   });
   $('#scrollbottom').hover(function() {
      $(this).stop().fadeTo('slow',1);
   },
   function() {
      $(this).stop().fadeTo('slow',0.5);
   });
});

function scrollToTop(id){
    $('html,body').animate({scrollTop: $("#"+id).offset().top},'slow');
};
