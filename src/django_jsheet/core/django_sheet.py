from django.urls import reverse_lazy


class DjangoSheet:
    """
    :param header: header of sheet (th), this param set the lenght of sheet
    :type header: list
    :param jquery: (QuerySet, form_class.base_fields)
    :type jquery: tuple

    :return: [ReturnDescription]
    :rtype: [ReturnType]
    """
    force_clm = False

    def __init__(
            self,
            header,
            jquery,
            colWidths,
            alignWidths,
            empty_row,
            force_clm=force_clm,
    ):
        self.header = header
        self.jquery = jquery
        self.colWidths = colWidths
        self.alignWidths = alignWidths
        self.empty_row = empty_row
        self.force_clm = force_clm
        self.set_header = []

    @property
    def len_row(self):
        return len(self.jquery[0])

    @property
    def len_row_sum(self):
        return len(self.jquery[0]) + int(self.empty_row)

    @property
    def range_len_row(self):
        return range(self.len_row_sum)

    @property
    def len_clm(self):
        return len(self.header)

    @property
    def set_col_width(self):
        colWidths = []
        if not self.colWidths:
            for i in range(self.len_clm):
                colWidths.append(100)
        else:
            if isinstance(self.colWidths, str):
                self.colWidths = int(self.colWidths)
            if isinstance(self.colWidths, int):
                for i in range(self.len_clm):
                    colWidths.append(self.colWidths)
            if isinstance(self.colWidths, list):
                colWidths = self.colWidths
        return colWidths

    @property
    def set_cell(self):
        """
        :return:    {
                        "title": "txt",
                        "initial": "txt",
                        "query": "array",  # only with choices and modelChoices
                        "width": 160,
                        "align": "center",  # left, center, right
                        "input": "text",  # text, number, float, choices, modelChoices
                    }
        :rtype:     dict
        """
        data = []

        for i, label in enumerate(self.jquery[1].keys()):
            field = self.jquery[1][label]
            field_class = field.__class__.__name__

            # init cell dict
            cell = {
                "title": label,
                "initial": "",
                "width": self.set_col_width[i],
                "align": self.alignWidths,
            }

            # set all types
            if field_class == 'CharField':
                cell["input"] = "text"
            if field_class == 'FloatField':
                cell["input"] = "text"
            if field_class == 'DateTimeField' or field_class == 'DateField':
                cell["input"] = "datetime-local"
            if field_class == 'FileField':
                cell["input"] = "file"
            if field_class == 'TypedChoiceField':
                cell["input"] = "__choices__"
                cell["query"] = getattr(self.jquery[0][0].__class__, label).field.choices
            if field_class == 'ModelChoiceField':
                cell["input"] = "__select__"
                # set default empty select
                cell["query"] = [("0", "None")]
                if len(self.jquery[0]) >= 1:
                    model_ = getattr(self.jquery[0][0], label).__class__
                    if model_.__name__ != "NoneType":
                        cell["title"] = model_.__name__
                        cell["query"] = [(x.pk, x.__str__()) for x in model_.objects.all()]

            data.append(cell)
        return data

    @property
    def dict_jsheet(self):
        return {
            "class_table": None,
            "setup": {
                "n_clm": self.len_clm,
                "n_row": (self.len_row, self.empty_row),
            },
            "header": self.header_sheet,
            "body": self.init_data,
            "jsrows": self.js_script_row,
            "jsfooter": self.jsrequest_post,
        }

    @property
    def header_sheet(self):
        thead = []
        for i, value in enumerate(self.header):
            header_ = {
                "title": value.capitalize(),
                "value": value,
                "width": self.set_col_width[i],
                "align": self.alignWidths,
            }
            thead.append(header_)
        return thead

    @property
    def init_data(self):
        if isinstance(self.jquery, tuple):
            query = self.jquery[0]
            order_by = list(self.jquery[1].keys())
        else:
            raise

        init_data = {}
        for i, g in enumerate(query):
            data = []
            # TODO: if form has '__all__' in field, what do you do?
            if isinstance(order_by, list):
                for j, x in enumerate(order_by):
                    value_dict = self.set_cell[j]
                    value = getattr(g, x)
                    if value:
                        if value_dict["input"] == "__select__":
                            value_dict["initial"] = value.pk
                        else:
                            value_dict["initial"] = value

                    data.append(value_dict)
            init_data[g.pk] = data

        for g in range(self.empty_row):
            init_data[f"empty_{g}"] = self.set_cell

        return init_data

    @property
    def js_script_row(self):
        # TODO: replace static splice with dynamic splice:
        #   get all input select and splice values in row_v
        js_script = ""
        for i in self.range_len_row:
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
            # insert model and choice value
            js_script += """ 
                        row_v.splice(1, 0, document.getElementById('User{0}').value.toString())
                        row_v.splice(5, 0, document.getElementById('InvoiceReceiptTypology{0}').value)
                        row_v.splice(6, 0, document.getElementById('PaymentMethod{0}').value)
                        row_v.splice(8, 0, document.getElementById('PaymentMethod{0}').value)
            """.format(i)
            # run update_rows to send request POST
            js_script += """
                        update_rows(row_v, %s);
                    });
                </script>
            """ % i
        return js_script

    @property
    def jsrequest_post(self):
        # TODO: add check login required
        return """
        <script src="https://code.jquery.com/jquery-3.5.1.js"
                integrity="sha256-QWo7LDvxbWT2tbbQ97B53yJnYU3WhH/C8ycbRAkjPDc="
                crossorigin="anonymous">
        </script>
        
        <script type="text/javascript">
        function update_rows(row, n_row) {
            $.ajax({
                type: 'POST',
                url: '%s',
                data: {
                    row_value:row.toString(),
                    csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
                },
                success: function (data) {
                    if (document.getElementById('hidden_row_empty_' + n_row)) {
                        document.getElementById('hidden_row_empty_' + n_row).setAttribute('id', 'hidden_row_' + n_row);
                        document.getElementById('hidden_row_' + n_row).value = data.result.success;
                    }
                },
                failure: function (errMsg) {
                    console.log(errMsg);
                }
            })
        }
        </script>
        """ % reverse_lazy("office-financial-invoice-receipt-sheet")

    @property
    def jsformulas(self):
        return """
            var formulas = {
                "sum"
                /**
                 * Custom method: SUM - Example: =SUM(C1:C10), =SUM(A1,A2,A3)
                 *
                 * @param string formula
                 * @return total
                 */
                : function (formula) {
                    // Get main table id
                    var id = $(this.instance).prop('id')
                    // Total to be returned
                    var total = 0
                    // Check sum type
                    var d = formula.split(/:/)
                    // Which sum to be used
                    if (d.length < 2) {
                        // Explode by comman and sum all columns in the formula
                        d = formula.split(',')
                        $.each($(d), function (k, v) {
                            v = parseInt($('#' + id).jexcel('getValue', v))
                            total += v
                        })
                    } else {
                        t1 = d[0].match(/[a-zA-Z]+/g)
                        t2 = d[1].match(/[a-zA-Z]+/g)
                        // Sum vertical or horizontal
                        if (t1[0] == t2[0]) {
                            // Some all cells in a vertical way
                            co = t1
                            t1 = d[0].match(/[0-9]+/g)
                            t2 = d[1].match(/[0-9]+/g)
                            for (i = t1; i <= t2; i++) {
                                v = parseInt($('#' + id).jexcel('getValue', co + i))
                                total += v
                            }
                        } else {
                            // Som all cells in a horizontal way
                            t1 = $('#' + id).jexcel('id', d[0]).split('-')
                            t2 = $('#' + id).jexcel('id', d[1]).split('-')
            
                            for (i = t1[0]; i <= t2[0]; i++) {
                                v = parseInt($('#' + id).jexcel('getValue',
                                                                i + '-' + t1[1]))
                                total += v
                            }
                        }
                    }
            
                    try {
                        return total
                    } catch (e) {
                        return null
                    }
                }
            }
        """
