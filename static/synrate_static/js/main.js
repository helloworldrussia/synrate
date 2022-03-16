$(document).ready(function() {


// kategories

$('.nav__link_list').on('click', function() {
	$('.categories-block').slideToggle('categories-block_active');
  });



$('.nav__link_mobile').on('click', function() {
	$('.categories-block_mobile').slideToggle('categories-block_mobile_active');
  });
// User 

$('.user-block__btn').on('click', function() {
	$('.user-block__btn_active').removeClass('user-block__btn_active')
	$('.user-block-list').addClass('user-block-list_active');
  });

$('.user-block-list-button').on('click', function() {
	$('.user-block-list').removeClass('user-block-list_active')
	$('.user-block__btn').addClass('user-block__btn_active');
  });


//faq


// Form input password

$('.input-password__btn').on('click', function(){
	if ($('#id_password1').attr('type') == 'password'){
		$(this).addClass('input-password__btn_active');
		$('#id_password1').attr('type', 'text');
	} else {
		$(this).removeClass('input-password__btn_active');
		$('#id_password1').attr('type', 'password');
	}
	if ($('#id_password').attr('type') == 'password'){
		$(this).addClass('input-password__btn_active');
		$('#id_password').attr('type', 'text');
	} else {
		$(this).removeClass('input-password__btn_active');
		$('#id_password').attr('type', 'password');
	}
	return false;
});



//filtrs tabs

$('.filtr-btn').on('click', function (e) {
    e.preventDefault();
    let currTab = $(this).index();
    $('.filtr-btn').removeClass('filtr-btn_active');
    $(this).addClass('filtr-btn_active');
});



// burger-menu
$('.mobile-menu__btn').on('click', function() {
	$('.mobile-menu-block').slideToggle('mobile-menu-block_active');
  });

// list Cabinet 

$('.cabinet-menu_mini').on('click', function() {
	$('.cabinet-menu-block-mini').toggle('cabinet-menu-block-mini_active');
  });





// Спойлер FAQ

$('.faq-questions__title').click(function() {
	$(this).toggleClass('active').next().slideToggle(300);
})

})










