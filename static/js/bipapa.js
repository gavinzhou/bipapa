$(function(){
var $container = $('#container');
$container.imagesLoaded(function(){
  $container.masonry({
    itemSelector : '.item',
  });
});
	
$container.infinitescroll({
	navSelector		: '#page-nav',
	nextSelector	: '#page-nav a:first',
	itemSelector	: '.item',
	loading:{
		finishedMsg: 'Nothing!!',
		img: 'http://i.imgur.com/6RMhx.gif',
	}
},
	
function( newElements ){
	var $newElems = $( newElements ).css({ opacity: 0 });
	$newElems.imagesLoaded(function(){
		$newElems.animate({ opacity: 1});
		$container.masonry( 'appended', $newElems, true);		
	});
});	
});