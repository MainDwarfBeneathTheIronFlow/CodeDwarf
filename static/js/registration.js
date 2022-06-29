$.getScript(pathToProject + "/js/added.js");
document.querySelector('.flex_footer').style.height = '0px';

$(document).ready(function(){
    
    let pipes = document.getElementsByClassName("pipe");
    let Ot = pipes[0].offsetTop + 50;
    
    let pipeBlock = document.getElementById("pipeBlock");

    $("#feedBack").on("submit", function(){ 
      if(document.forms.feedBack.action.toString().slice(-2) == 'on') {

        $('.flex_footer').animate({
          'height' : "142px",
        }, {duration: durat*1000, queue: true});
          
        setTimeout(function () {
          $('.false_footer').animate({
          'opacity' : 0, }, 
          {duration: 1000, queue: true})}, 
        durat * 1 * 1000);

        mainCanvas.style.display = "block";
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        let pipeMove = pipeBlock.offsetTop;

        setInterval(function(){
          if(pipeMove < 0) {
            emitters = [];
            Array.from(pipes).forEach(function(element){
              emitters.push(new Emitter(new Vector(element.offsetLeft + 80, Ot + pipeMove/2), Vector.fromAngle(1.55, 15), -0.2));
            });
            pipeMove += 2;
            pipeBlock.style.top = pipeMove + "px";
            
          }
          
        }, 2)

        setTimeout(function () {
            emitters = [];
            $('.flex_header').animate({
              'height' : '0%', 
              'padding': '0px',}, 
            {duration: 1000, queue: false});

            pipeBlock.animate({
              'top' : '-160px',
            }, {duration: 1000, queue: false});

            setTimeout(() => pipeBlock.style.top = '-160px', 1000);
        },  durat * 700);
        
        loop();
      }
    });


    
    // Login
    let toLogin = document.forms.toLogin;
    let toReg = document.forms.toRegistrarion;

    $("#toLogin").on("submit", function(){
      document.forms.feedBack.action = '/login';
      toLogin.className = "activated";
      toReg.className = "inactivated";
      console.log(document.forms.feedBack.action);
    });
    $("#toRegistrarion").on("submit", function(){
      document.forms.feedBack.action = '/registration';
      toLogin.className = "inactivated";
      toReg.className = "activated";
      console.log(document.forms.feedBack.action);
    });
})  
