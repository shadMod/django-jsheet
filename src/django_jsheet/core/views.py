import os
import json
import traceback

from datetime import datetime
from logging import getLogger

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

logger = getLogger(__name__)


class DjangoSheetFormView(FormView):
    HISTORY: bool = True
    LOGROOT: str = None
    SVIL: bool = False
    TIME_UPDATE: int = 10000  # 10000 => 10 sec
    SYNC_DB: bool = False
    empty_row: int = 10
    header = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.header:
            self.header = list(self.form_class.base_fields.keys())

        self.jspath = self.mk_jspath()
        self.jsdata = self.jspath + "/data.js"

        if settings.DEBUG:
            self.SVIL = True

        if self.HISTORY:
            # make and populate file log (first populate)
            self.path_filelog, self.filelog = self.mk_file_log()
            self.populate_log()

        if self.SYNC_DB:
            # prepopulate js with data model
            self.make_data_js()

        # read populate file log
        self.jsheadersheet()

        if self.HISTORY:
            # populate file log
            # TODO: code
            # clean all populate file log (without latest)
            # TODO: code
            pass

    def dispatch(self, *args, **kwargs):
        # added fetch post file
        self.make_fetch_js()

        if self.request.method == "POST":
            res, msg = self.save()
            if res:
                result = {
                    "result": {
                        "success": msg,
                    },
                }
                json_data = json.dumps(result)
                return HttpResponse(json_data, content_type="application/json")
            else:
                logger.error(msg)
        return super().dispatch(*args, *kwargs)

    def save(self):
        try:
            data_row = json.loads(self.request.body.decode("utf-8"))
        except Exception as ex:
            logger.error(traceback.format_exc())
            return False, ex

        data = []
        for i, row in data_row.items():
            data.append(row)

        try:
            self.make_data_js(data)
        except Exception as ex:
            logger.error(traceback.format_exc())
            return False, ex

        return True, "ok"

    def mk_jspath(self):
        jspath = str(self.LOGROOT) + "/jsheet/js/"
        if not os.path.exists(jspath):
            os.makedirs(jspath)
        return jspath

    def mk_file_log(self):
        path_logs = str(self.LOGROOT) + "/jsheet/"
        if not os.path.exists(path_logs):
            os.makedirs(path_logs)

        if self.SVIL:
            now_ = datetime.now().strftime("%d%m%Y")
        else:
            now_ = datetime.now().strftime("%d%m%Y_%H%M%S")
        # init filelog
        filelog = path_logs + "datalog_" + now_ + ".json"

        f = open(filelog, "w")
        f.close()
        return path_logs, filelog

    def jsheadersheet(self):
        datajs = """
			jspreadsheet(document.getElementById('spreadsheet'), {
				data:data, columns: 
		"""
        header = []
        type_header = ""
        for i, field in enumerate(self.form_class.base_fields.values()):
            # set field name
            field_name = field.__class__.__name__
            if field_name == "CharField":
                type_header = (
                    """
                        {
                            type: 'text',
                            title: '%s',
                            width: 400
                        },
                    """
                    % self.header[i]
                )
                type_header = "".join(type_header.split())
            if field_name == "FloatField":
                type_header = (
                    """
                        {
                            type: 'numeric',
                            title: '%s',
                            mask: '€ #.##,00',
                            width: 120,
                            decimal: ','
                        },
                    """
                    % self.header[i]
                )
                type_header = "".join(type_header.split())
            if field_name == "DateTimeField" or field_name == "DateField":
                type_header = (
                    """
                        {
                            type: 'calendar',
                            title: '%s',
                            width: 120
                        },
                    """
                    % self.header[i]
                )
                type_header = "".join(type_header.split())
            if field_name == "FileField":
                type_header = (
                    """
                        {
                            type: 'text',
                            title: '%s',
                            width: 400
                        },
                    """
                    % self.header[i]
                )
                type_header = "".join(type_header.split())
            if field_name == "TypedChoiceField":
                source = [x[1] for x in field._choices]
                type_header = """
					{
						type: 'dropdown',
						title: '%s',
						width: 150,
						source: %s
					}
				""" % (
                    self.header[i],
                    source,
                )
                type_header = " ".join(type_header.split())
            if field_name == "ModelChoiceField":
                source = [x.__str__() for x in field._queryset]
                type_header = """
					{
						type: 'dropdown',
						title: '%s',
						width: 150,
						source: %s
					}
				""" % (
                    self.header[i],
                    source,
                )
                type_header = " ".join(type_header.split())
            header.append(type_header)

        datajs += str(header).replace('"', "").replace(",,", ",") + "})"
        jsfile = self.jspath + "/header.js"
        with open(jsfile, "w") as fl:
            fl.write(datajs)

    def make_data_js(self, data: str = None):
        """
        var data = [
            ['50', 'Robe', 'casa', 'carta', '2019-02-12', 'non pagato'], real data value
            ['', '', '', '', '', ''], empty row (set in init)
        ];
        """
        # init datajs
        datajs = "var data = "
        if not data:
            # open data
            datajs += "["
            # prepopulate datajs if exist model and data row in model
            datajs += self.prepopulate_datajs()
            # write empty row
            for i in range(self.empty_row):
                datajs += str(["" for x in range(len(self.header))]) + ","
            # close datajs
            datajs += "];"
        else:
            datajs += str(data)

        with open(self.jsdata, "w") as fl:
            fl.write(datajs)

    def prepopulate_datajs(self):
        datajs = ""
        for value in self.model.objects.all():
            list_vl = []
            for key_, field in self.form_class.base_fields.items():
                # get value
                vl = getattr(value, key_)

                # set field name
                field = field.__class__.__name__
                if field == "CharField":
                    list_vl.append(str(vl))
                if field == "FloatField":
                    list_vl.append(str(vl))
                if field == "DateTimeField" or field == "DateField":
                    list_vl.append(str(vl.strftime("%Y-%m-%d")))
                if field == "FileField":
                    list_vl.append(str(vl))
                if field == "TypedChoiceField":
                    choices = getattr(self.model, key_).field.choices
                    vl = dict(choices)[vl]
                    list_vl.append(str(vl))
                if field == "ModelChoiceField":
                    list_vl.append(str(vl))
            datajs += str(list_vl) + ","
        return datajs

    def populate_log(self):
        datalog = {}
        for key in self.form_class.base_fields.keys():
            datalog[key] = ""

        with open(self.filelog, "w") as fl:
            fl.write(json.dumps(datalog))

    def make_fetch_js(self):
        # get current url and relative path url
        current_url = self.request.resolver_match.view_name
        post_url = reverse_lazy(current_url)

        # make fetch post JS
        fetch_post = """
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
                    var cookie = jQuery.trim(cookies[i]);
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
        """ % (self.TIME_UPDATE, post_url)

        # make and put scripts in fetch_post.js in jspath dir
        jsfile = self.jspath + "/fetch_post.js"
        with open(jsfile, "w") as fl:
            fl.write(fetch_post)
