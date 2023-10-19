/* при прокрутке странице вызовем scrollFunction*/
window.onscroll = function() { scrollFunction()};

/* если от верхней части страницы прокрутки больше, чем 200px*/
function scrollFunction() {
    if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
        document.getElementById("top-btn").style.display = "block";
    }
    else {
     document.getElementById("top-btn").style.display = "none";
    }
}


function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}