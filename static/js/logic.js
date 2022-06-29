let news_id = "";
let news_viewer = $('.news_viewer');
let news_block = $('.news_block');

const news_mainblock = document.querySelector('.news_block');


$(document).ready(function(){

    let backFunc;
    if(pageCond == "news") {
        backFunc = "/post/"
    }
    else {
        backFunc = "/game/"
    }
    news_mainblock.addEventListener("click", function(event) {

        if(event.target.closest('.news_element')) {
            if(event.target.closest('.news_element').id != news_id) {
                news_block.animate({width: "160px"}, {duration:200, queue: false});

                news_viewer.animate({     
                    width: '840',
                    padding: 20,
                }, {duration: 1000, queue: false});


                news_id = event.target.closest('.news_element').id;
                myId = event.target.closest('.news_element').id;
                $.ajax({
                    url: backFunc + myId.replace(pageCond, ''),
                    type: "get",
                    dataType: "json",
                    data: JSON.stringify({
                        title: "updatetitle",
                    }),
                    success: function(data) {
                        document.querySelector('.news_viewer').innerHTML = data;
                    }
                });
                console.log(news_id);
            } 
            else {
                news_viewer.animate({     
                    width: 0,
                    padding: 0,
                }, {duration:200, queue: false});
                
                news_block.animate({width: "1000px"}, {duration:1000, queue: false});
                news_id = "";
            }
        }
    });
});