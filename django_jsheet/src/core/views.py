import os
import json
import traceback

from datetime import datetime
from logging import getLogger

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .constats import column_header, get_fetch_js

logger = getLogger(__name__)


class DjangoSheetFormView(FormView):
    """
    :model:         add model (not required)
    :header:        set header column (not required)
    :empty_row:     set number of empty row post data
                    (N.B. they are initialized when the first data.js is created)

    :HISTORY:       if True make and populate filelog with edit history
    :LOGROOT:       populate with the root path where we are going to load
                    the various static script files
    :SVIL:          if True active debug mode; if settings.DEBUG is True SVIL
                    will be regardless true
    :TIME_UPDATE:   determines how often you want to save resources
                    (eg 10000 = 10 sec)
    :SYNC_DB:       if True all changes will also go to save in the DB
    """
    model: str = None
    header: list = None
    empty_row: int = 10

    HISTORY: bool = False
    LOGROOT: str = None
    SVIL: bool = False
    TIME_UPDATE: int = 10000
    SYNC_DB: bool = False

    def __init__(self, *args, **kwargs):
        super(DjangoSheetFormView, self).__init__(*args, **kwargs)
        if not self.header:
            self.header = list(self.form_class.base_fields.keys())
        else:
            self.header_validator()

        self.jspath = self.mk_jspath()
        self.jsdata = self.jspath + "/data.js"

        if settings.DEBUG is True:
            self.SVIL = True

        # init file log paths
        if self.HISTORY:
            self.path_filelog, self.filelog = self.mk_file_log()
        else:
            self.path_filelog, self.filelog = None, None

        # make data.js with data model and empty rows
        self.make_data_js(sync_db=self.SYNC_DB)

        # read populate file log
        self.jsheadersheet()

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
            self.make_data_js(data, self.SYNC_DB)
        except Exception as ex:
            logger.error(traceback.format_exc())
            return False, ex

        if self.HISTORY:
            self.populate_log()

        return True, "ok"

    def header_validator(self) -> None:
        nr_header = len(self.header)
        nr_base_fields = len(self.form_class.base_fields.keys())
        if nr_header != nr_base_fields:
            if nr_header > nr_base_fields:
                self.header = self.header[nr_base_fields]
            if nr_header < nr_base_fields:
                self.header.extend(["" for _ in range(nr_base_fields - nr_header)])

    def mk_jspath(self) -> str:
        jspath = str(self.LOGROOT) + "/jsheet/js/"
        if not os.path.exists(jspath):
            os.makedirs(jspath)
        return jspath

    def mk_file_log(self) -> (str, str):
        path_logs = str(self.LOGROOT) + "/jsheet/"
        if not os.path.exists(path_logs):
            os.makedirs(path_logs)

        if self.SVIL:
            now_ = datetime.now().strftime("%d%m%Y")
        else:
            now_ = datetime.now().strftime("%d%m%Y_%H%M%S")
        # init filelog
        filelog = path_logs + "datalog_" + now_ + ".log"
        return path_logs, filelog

    def make_data_js(self, data: list = None, sync_db: bool = False) -> None:
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
            if sync_db:
                # prepopulate/sync datajs if exist model and data row in model
                datajs += self.prepopulate_datajs()
                datajs += self.get_emtpy_row()
            elif self.filelog and os.path.exists(self.filelog):
                with open(self.filelog) as fn:
                    last_log = fn.readlines()[-1]
                datajs += last_log.split("_GMT__")[1]
                # write empty row
                if not os.path.exists(self.filelog):
                    datajs += self.get_emtpy_row()
            elif os.path.exists(self.jsdata):
                with open(self.jsdata) as fn:
                    datajs += fn.read().replace("var data = [", "").replace("']];", "']")
            else:
                datajs += self.get_emtpy_row()
            datajs += "];"
        else:
            datajs += str(data) + ";"

        with open(self.jsdata, "w") as fl:
            fl.write(datajs)

    def prepopulate_datajs(self):
        datajs = ""
        for value in self.model.objects.all():
            list_vl = []
            for key, field in self.form_class.base_fields.items():
                # get value
                vl = getattr(value, key)

                # set field name
                field = field.__class__.__name__
                if field == "CharField":
                    list_vl.append(str(vl))
                if field == "IntegerField":
                    list_vl.append(str(vl))
                if field == "FloatField":
                    list_vl.append(str(vl))
                if field == "DecimalField":
                    list_vl.append(str(vl))
                if field == "DateField":
                    list_vl.append(str(vl.strftime("%Y-%m-%d")))
                if field == "DateTimeField":
                    list_vl.append(str(vl.strftime("%Y-%m-%d")))
                if field == "FileField":
                    list_vl.append(str(vl))
                if field == "TypedChoiceField":
                    choices = getattr(self.model, key).field.choices
                    vl = dict(choices)[vl]
                    list_vl.append(str(vl))
                if field == "ModelChoiceField":
                    list_vl.append(str(vl))
            datajs += str(list_vl) + ","
        return datajs

    def populate_log(self):
        with open(self.jsdata) as fn:
            datalist = fn.read().replace("var data = ", "")

        datalog = datalist.replace("[['", "['").replace("']];", "']")

        mode = "a" if os.path.exists(self.filelog) else "w"
        space_txt = "\n" if mode == "a" else ""
        with open(self.filelog, mode=mode) as fl:
            log_rows = (
                    datetime.now().strftime(space_txt + "%d/%m/%Y_%H:%M:%S_GMT__") + datalog
            )
            fl.write(log_rows)

    def get_emtpy_row(self, nr_row: int = None) -> str:
        if nr_row is None:
            nr_row = self.empty_row

        empty_row = str(["" for _ in range(len(self.header))])
        return ",".join([empty_row for _ in range(nr_row)])

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
                type_header = column_header("CharField", self.header[i])
            if field_name == "IntegerField":
                type_header = column_header("IntegerField", self.header[i])
            if field_name == "FloatField":
                type_header = column_header("FloatField", self.header[i])
            if field_name == "DecimalField":
                type_header = column_header("DecimalField", self.header[i])
            if field_name == "DateField":
                type_header = column_header("DateField", self.header[i])
            if field_name == "DateTimeField":
                type_header = column_header("DateTimeField", self.header[i])
            if field_name == "FileField":
                type_header = column_header("FileField", self.header[i])
            if field_name in ["ChoiceField", "TypedChoiceField"]:
                source = [x[1] for x in field._choices]
                type_header = column_header(
                    "TypedChoiceField", self.header[i], source
                ).replace("'['", "['").replace("']'", "']")
            if field_name == "ModelChoiceField":
                source = [x.__str__() for x in field._queryset]
                type_header = column_header(
                    "ModelChoiceField", self.header[i], source
                ).replace("'['", "['").replace("']'", "']")
            header.append(type_header)

        datajs += str(header).replace('"', "").replace(",,", ",") + "})"
        jsfile = self.jspath + "/header.js"
        with open(jsfile, "w") as fl:
            fl.write(datajs)

    def make_fetch_js(self):
        # get current url and relative path url
        current_url = self.request.resolver_match.view_name
        post_url = reverse_lazy(current_url)

        # make fetch post JS
        fetch_post = get_fetch_js() % (self.TIME_UPDATE, post_url)

        # make and put scripts in fetch_post.js in jspath dir
        jsfile = self.jspath + "/fetch_post.js"
        with open(jsfile, "w") as fl:
            fl.write(fetch_post)
