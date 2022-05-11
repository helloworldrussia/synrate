$(document).ready(function(){

    fix_logos();
    fix_header();

});
$(window).on('load resize',function (){
    fix_logos();
});

function fix_header(){
    if($(document).find(".header_padding").length){
        $(document).find(".header_padding").height($(document).find(".header").outerHeight());
    }
}

function fix_logos(){
    if($(document).find(".offer-block__img").length){
        $(document).find(".offer-block__img").each(function (){
            $(this).removeClass('resizeds').stop();
            var _th = $(this).outerHeight()+10;
            if(_th>=$(this).parent().outerHeight()){
                $(this).addClass('resizeds');
            }
        })
    }
}
