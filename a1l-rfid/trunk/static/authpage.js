var req = new XMLHttpRequest();

function wait_for_tag() {
    req.onreadystatechange = rfscan_result;
    check_rfscan();
}

function check_rfscan() {
    req.open("GET","/last-rfid", true);
    req.send(null);
}

function rfscan_result() {
    document.getElementById('results').innerHTML=req.readyState + ", "+req.status;
    if (req.readyState < 4)
    {
       return;
    }
    if (req.status == 200)
    {
        alert(req.responseText);
        var rfid_text = document.getElementById("tag_id");
        rfid_text.text = req.responseText;
    }
    window.setTimeout("check_rfscan()", 500);
}
