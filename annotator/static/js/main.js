/*if the user clicks anywhere outside the select box,
then close all select boxes:*/


$(".image-checkbox").each(function () {
    if ($(this).find('input[type="checkbox"]').first().attr("checked")) {
        $(this).addClass('image-checkbox-checked');
    } else {
        $(this).removeClass('image-checkbox-checked');
    }
});

// sync the state to the input
$(".image-checkbox").on("click", function (e) {
    $(this).toggleClass('image-checkbox-checked');
    var $checkbox = $(this).find('input[type="checkbox"]');
    $checkbox.prop("checked", !$checkbox.prop("checked"));
    e.preventDefault();
});

$('#image').flexImages({truncate: 1});

if (~window.location.href.indexOf('http')) {
    (function () {
        var po = document.createElement('script');
        po.type = 'text/javascript';
        po.async = true;
        po.src = 'https://apis.google.com/js/plusone.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(po, s);
    })();
    (function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s);
        js.id = id;
        js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.4&appId=114593902037957";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
    !function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0], p = /^http:/.test(d.location) ? 'http' : 'https';
        if (!d.getElementById(id)) {
            js = d.createElement(s);
            js.id = id;
            js.src = p + '://platform.twitter.com/widgets.js';
            fjs.parentNode.insertBefore(js, fjs);
        }
    }(document, 'script', 'twitter-wjs');
}


function openView(id) {
    window.open('OBJViewer?fileURL=/zip/' + id);
}

function toggleNav() {
    console.log(document.getElementById("mySidenav").style.width);
    if (document.getElementById("mySidenav").style.width !== "0px") {
        closeNav()
    } else {
        openNav()
    }
}

function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}

function removeElement(elementId) {
    // Removes an element from the document
    var element = document.getElementById(elementId);
    element.parentNode.removeChild(element);
}

function getCheckedBoxes(chkboxName) {
    var checkboxes = document.getElementsByName(chkboxName);
    var checkboxesChecked = [];
    // loop over them all
    for (var i = 0; i < checkboxes.length; i++) {
        // And stick the checked ones onto an array...
        if (checkboxes[i].checked) {
            checkboxesChecked.push(checkboxes[i].value);
        }
    }
    // Return the array if it is non-empty, or null
    return checkboxesChecked.length > 0 ? checkboxesChecked : null;
}

// Call as

function changeItem() {
    var xhr = new XMLHttpRequest();
    var checkedBoxes = getCheckedBoxes("image");

    xhr.open("POST", "/filter", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        "keyword": keyword,
        "ids": checkedBoxes,
        "label": -1,
    }));
    for (i = 0; i < checkedBoxes.length; i++) {
        removeElement(checkedBoxes[i]);
    }
}

function annotateItem() {
    var xhr = new XMLHttpRequest();
    var e = document.getElementById('label');
    var label = e.options[e.selectedIndex].value;
    var checkedBoxes = getCheckedBoxes("image");

    xhr.open("POST", "/filter", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        "keyword": keyword,
        "ids": checkedBoxes,
        "label": label,
    }));
    for (i = 0; i < checkedBoxes.length; i++) {
        removeElement(checkedBoxes[i]);
    }
}

