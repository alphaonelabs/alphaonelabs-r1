var req = new XMLHttpRequest();
function waitfortag() {
    check_rfscan();
}

function check_rfscan() {
    req.onreadystatechange = rfscan_result;
    req.open("GET","/last-rfid", true);
    req.send(null);
}

function rfscan_result() {
    if (req.readyState < 4)
    {
       return;
    }
    if (req.status == 200)
    {
        var rfid_text = document.getElementById("tag_id");
        rfid_text.text = req.responseText;
    }
    window.setTimeout("check_rfscan()", 500);
}
