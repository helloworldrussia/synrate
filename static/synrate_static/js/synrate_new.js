$(document).ready(function(){

    fix_logos();

});
$(window).on('load resize',function (){
    fix_logos();
});

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
