setInterval(function() {get_rows_table()}, %s)

function get_rows_table() {
    var t = document.getElementsByClassName('jexcel')[0]
    var trs = t.getElementsByTagName("tr");
    var tds = null;

    var data_j = {};
    for (var i=1; i<trs.length; i++)
    {
        array_data = [];
        tds = trs[i].getElementsByTagName("td");
        for (var n=1; n<tds.length;n++)
        {
            array_data.push(tds[n].innerHTML);
        };
        data_j[i] = array_data;
    }
    update_rows(data_j)
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function update_rows(data_j) {
    fetch("%s", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data_j)
        }
    ).then(res => {
            <!--console.log("Request complete!");-->
        }
    );
}