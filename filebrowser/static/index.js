$(function () {
    $(".type-des-pic").parents("td").css("cursor","pointer").on("click",function (event) {
        const img_url = $(this).children("img").attr("src");
        $.each($(".type-des-pic"),function(index,item){
            const img_div = $("<div>").addClass("carousel-item img_preview").append($("<img>").attr("src",item.src))
            if($(item).attr("src") == img_url) img_div.addClass("active")
            img_div.appendTo($("#carousel1>.carousel-inner"))
        })
        $(".modal").modal('show');

    })
})