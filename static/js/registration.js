$(document).ready(function(){
    $.getScript(pathToProject + "/js/added.js");
    


    document.getElementById('footer').style.height = "0%";
    $("#feedBack").on("submit", function(){ 

        $('.flex_footer').animate({
          "height" : "10%",
        }, {duration: durat*1000, queue: true});
          
        setTimeout(function () {
          $('.false_footer').animate({
          'opacity' : 1, }, 
          {duration: 1000, queue: true})}, 
        durat * 1 * 1000);

        mainCanvas.style.display = "block";
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        emitters = [new Emitter(new Vector(midX, 0), Vector.fromAngle(1.55, 15), -0.2),
            new Emitter(new Vector(10, 0), Vector.fromAngle(1.55, 15), -0.2),
            new Emitter(new Vector(canvas.width-10, 0), Vector.fromAngle(1.55, 15), -0.2)];

        setTimeout(function () {
            emitters = [];
            $('.flex_header').animate({
                'height' : '0%', 
                'padding': '0px',}, 
                {duration: 1000, queue: true})
        },  durat * 700);
        
        loop();
    })
})  

