$(document).ready(function(){
    document.getElementById("preview").src = pathToProject + "/avatars/" + avatarName;
    document.getElementById("miniPreview").src = pathToProject + "/avatars/" + avatarName; 

    let toProfile = document.forms.toProfile;
    let toOptions = document.forms.toOptions;
    let profileList = document.getElementById("profileList");
    let profileViewer = document.getElementById("profileViewer");
    let setSupervisor = document.getElementById("setSupervisor");

    $("#toProfile").on("submit", function(){
      toProfile.className = "activated";
      toOptions.className = "inactivated";
      profileViewer.style.visibility = "visible";
      profileList.style.visibility = "collapse";
    });
    $("#toOptions").on("submit", function(){
      toProfile.className = "inactivated";
      toOptions.className = "activated";
      profileViewer.style.visibility = "collapse";
      profileList.style.visibility = "visible";
      setSupervisor.placeholder = "Cубъект обнаружил в себе магию?";
    });

    
})