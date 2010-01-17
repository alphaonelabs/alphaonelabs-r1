var req = new XMLHttpRequest();

function wait_for_tag() {
    req.onreadystatechange = rfscan_result;
    check_rfscan();
}

function check_rfscan() {
    try {
        req.open("GET","/last-rfid", true);
        req.send(null);
    } catch (e) {
        alert(e);
    }
}

function rfscan_result() {
    document.getElementById('results').innerHTML=req.readyState + ", "+req.status;
    var rfid_text = document.getElementById("tag_id");

    if (req.readyState < 4)
    {
       return;
    }
    if (req.status == 200)
    {
        document.getElementById('results').innerHTML=req.responseText;
        rfid_text.value = req.responseText;
    }
    if (rfid_text.value == "")
        window.setTimeout("check_rfscan()", 500);
}
