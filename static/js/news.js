let news_id = "";
let news_viewer = $('.news_viewer');
let news_block = $('.news_block');


const news_mainblock = document.querySelector('.news_block');

let newsElements = document.getElementsByClassName("news_element");
let addedImages = "";
Array.from(newsElements).forEach(function(el){
    addedImages += "." + el.id + "::before{ background-image: url(" + pathToProject + "/news/" + el.id + ".png)}";
});
var styleElem = document.head.appendChild(document.createElement("style"));
// styleElem.innerHTML = addedImages;

news_mainblock.addEventListener("click", function(event) {
    // if(event.target.closest('.news_element')) {
    //     myId = event.target.closest('.news_element').id;
    //     $.ajax({
    //         url: "/post/" + myId,
    //         type: "get",
    //         dataType: "json",
    //         data: JSON.stringify({
    //             title: updatetitle,
    //         }),
    //         success: function(data) {
    //             alert(title);
    //         }
    //     });
    // }





    // if(event.target.closest('.news_element')) {
    //     if(event.target.closest('.news_element').id != news_id) {
    //         news_block.animate({width: "160px"}, {duration:200, queue: false});

    //         news_viewer.animate({     
    //             width: '840',
    //             padding: 20,
    //         }, {duration: 1000, queue: false});

    //         if(news_id)
    //             $.ajax({
    //                 url: pathToProject + "/news/" + news_id + ".js",
    //                 type: 'DELETE',
    //             });

    //         news_id = event.target.closest('.news_element').id;
    //         $.getScript(pathToProject + "/news/" + news_id + ".js")
    //         console.log(news_id);
    //     } 
    //     else {
    //         news_viewer.animate({     
    //             width: 0,
    //             padding: 0,
    //         }, {duration:200, queue: false});

    //         $.ajax({
    //             url: pathToProject + "/news/" + news_id + ".js",
    //             type: 'DELETE',
    //         });
            
    //         news_block.animate({width: "1000px"}, {duration:1000, queue: false});
    //         news_id = "";
    //     }
    // }


    if(event.target.closest('.news_element')) {
        if(event.target.closest('.news_element').id != news_id) {
            news_block.animate({width: "160px"}, {duration:200, queue: false});

            news_viewer.animate({     
                width: '840',
                padding: 20,
            }, {duration: 1000, queue: false});

            // if(news_id)
            //     $.ajax({
            //         url: pathToProject + "/news/" + news_id + ".js",
            //         type: 'DELETE',
            //     });

            news_id = event.target.closest('.news_element').id;
            // $.getScript(pathToProject + "/news/" + news_id + ".js")
            myId = event.target.closest('.news_element').id;
            $.ajax({
                url: "/post/" + myId.replace('news', ''),
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