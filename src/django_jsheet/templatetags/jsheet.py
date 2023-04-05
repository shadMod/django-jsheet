from django import template
from django.utils.safestring import mark_safe

register = template.Library()

CSS_STYLE = """
    <style>
        input {
            width:100%;
            margin:0;
            background:transparent;
            border:0px solid #cccccc;
        }
        .input:focus {
            outline: none !important;
            border:1px solid red;
            box-shadow: 0 0 10px #719ECE;
        }
        .input:focus-visible {
            outline: none !important;
            border:1px solid red;
            box-shadow: 0 0 10px #719ECE;
        }
        table tr td {
            border-right:1px solid #cccccc;
            border-bottom:1px solid #cccccc;
        }
        table {
            background: #fff none repeat scroll 0 0;
            border-left: 1px solid #cccccc;
            border-top: 1px solid #cccccc;
        }

        select {
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            /* Remove default arrow */
            /* background-image: url(...); */
            /* Add custom arrow */
        }
    </style>
"""


@register.simple_tag
def display_jsheet(data: dict = None):
    if data is None:
        data = {
            "header": [],
        }

    # set thead
    thead = "<thead class='label'><tr><td width='30' class='label'></td>"
    for i, hd_ in enumerate(data["header"]):
        thead += """
            <td id="col-{i}" width="{width}" align="{align}" title="{value}">{value}</td>
        """.format(
            i=i,
            width=hd_.get("width", ""),
            align=hd_.get("align", ""),
            value=hd_.get("value", ""),
        )
    thead += "</tr></thead>"
    # set tbody
    tbody = "<tbody>"
    for i, key_ in enumerate(data["body"]):
        # init tr in tbody
        tbody += "<tr id='row_{0}'>".format(i)
        # set id class of hidden row
        if "empty_" in str(key_):
            id_class = "id='hidden_row_empty_{0}'".format(i)
        else:
            id_class = "id='hidden_row_{0}'".format(i)
        tbody += """
            <td id='clm-{0}' class='label'>{1}<input type='hidden' value='{2}' {3}></td>
        """.format(i, i + 1, key_, id_class)
        td_query = data["body"][key_]
        for td_ in td_query:
            if isinstance(td_, dict):
                tbody += "<td width='{width}' align='{align}'>".format(
                    width=td_.get("width", ""), align=td_.get("align", "")
                )
                input_type = td_.get("input", "")
                initial = td_.get("initial", "")
                # select ModelChoiceField
                if input_type == '__select__':
                    initial = td_.get("initial", "")
                    query = td_.get("query", "")
                    tbody += "<select id='{title}{i}'>".format(i=i, title=td_.get("title", ""))
                    for val_, label in query:
                        if str(initial) == str(val_):
                            target = "selected"
                        else:
                            target = ""
                        tbody += "<option value='{0}' {2}>{1}</option>".format(val_, label, target)
                    tbody += "</select></td>"
                # select TypedChoiceField
                elif input_type == "__choices__":

                    query = td_.get("query", "")
                    tbody += "<select id='Choices{i}'>".format(i=i)
                    for val_, label in query:
                        if str(initial) == str(val_):
                            target = "selected"
                        else:
                            target = ""
                        tbody += "<option value='{0}' {2}>{1}</option>".format(val_, label, target)
                    tbody += "</select></td>"
                else:
                    tbody += """
                        <input type="{input}" value="{value}"></td>
                    """.format(i=i, input=input_type, value=initial)
            else:
                raise
        tbody += "</tr>"
    tbody += "</tbody>"

    js_script = data.get("jsrows", "")
    jsfooter = data["jsfooter"]

    table = """
    {style}
    <div id="sheet">
        <table class='jexcel bossanova-ui' cellpadding='0' cellspacing='0' id='id_jsheet'>
        {thead}
        {tbody}
        </table>
    </div>
    
    {js_script}
    {jsfooter}
    """.format(
        style=CSS_STYLE, thead=thead, tbody=tbody, js_script=js_script, jsfooter=jsfooter,
    )
    return mark_safe(table)


def js_script_row(n_row, start: int = 0):
    js_script = ""
    for i in range(start, n_row):
        # init scripts
        js_script += """
            <script type="text/javascript">
                var clm_len = document.getElementById('id_jsheet').rows[0].cells.length;
        """
        # get number row and init row_v and append value clean
        js_script += """
                row_%s.addEventListener("input", function (e) {
                    var row_v = [];
                    for (var i = 0; i < 6; i++) {
                        row_v.push(this.getElementsByTagName('input')[i].value)
                    } 
        """ % i
        # insert model value
        js_script += """ 
                    row_v.splice(1, 0, document.getElementById('User{0}').value.toString())
                    row_v.splice(5, 0, document.getElementById('InvoiceReceiptTypology{0}').value)
                    row_v.splice(6, 0, document.getElementById('PaymentMethod{0}').value)
        """.format(i)
        # run update_rows to send request POST
        js_script += """
                    update_rows(row_v, %s);
                });
            </script>
        """ % i
    return js_script
