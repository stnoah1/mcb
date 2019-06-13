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
        }));
        for (i = 0; i < checkedBoxes.length; i++) {
            removeElement(checkedBoxes[i]);
        }
    }