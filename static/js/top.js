/* ��� ��������� �������� ������� scrollFunction*/
window.onscroll = function() { scrollFunction()};

/* ���� �� ������� ����� �������� ��������� ������, ��� 200px*/
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