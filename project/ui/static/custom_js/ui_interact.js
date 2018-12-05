// Get the Sidebar
var mySidebar = document.getElementById("mySidebar");
// Get the DIV with overlay effect
var overlayBg = document.getElementById("myOverlay");
// Toggle between showing and hiding the sidebar, and add overlay effect
function w3_open() {
    if (mySidebar.style.display === 'block') {
        mySidebar.style.display = 'none';
        overlayBg.style.display = "none";
    } else {
        mySidebar.style.display = 'block';
        overlayBg.style.display = "block";
    }
}
// Close the sidebar with the close button
function w3_close() {
    mySidebar.style.display = "none";
    overlayBg.style.display = "none";
}

function only_display(menu) {
    menus = {
        'gzh':document.getElementById("gzh-menu"),
        'crawler':document.getElementById("crawler-menu"),
        'settings':document.getElementById("settings-menu")};
    for (var key in menus){
        if(key==menu){
            menus[key].style.display = 'block';
        }
        else
        {
            menus[key].style.display = 'none';
        }
    }
}

//支持点击标题排序
// $(function() {
//     $("table")
//         .tablesorter({debug: false})
// });
//支持点击标题排序
$(document).ready(function(){
        setTimeout(function(){$("table").tablesorter();}, 100);
    }
);
