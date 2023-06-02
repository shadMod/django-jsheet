import os
import json

from datetime import datetime

from django.conf import settings
from django.views.generic.edit import FormView


class DjangoSheetFormView(FormView):
    HISTORY: bool = True
    LOGROOT: str = None
    SVIL: bool = False
    empty_row: int = 10
    header = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.header:
            self.header = list(self.form_class.base_fields.keys())

        if settings.DEBUG:
            self.SVIL = True

        if self.HISTORY:
            # check if exist populate file log
            # TODO: code
            # make and get populate file log (first populate)
            self.path_filelog, self.filelog = self.mk_file_log()
            self.populate_log()
            self.jspath = self.mk_jspath()
            # read populate file log
            self.make_data_js()
            self.jsheadersheet()

    # populate file log
    # TODO: code
    # clean all populate file log (without latest)
    # TODO: code

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jsheet"] = self.model.objects.all()
        return context

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

    def make_data_js(self):
        """
        var data = [
            ['50', 'Robe', 'casa', 'carta', '2019-02-12', 'non pagato'],
            ['', '', '', '', '', ''],
        ];
        """
        # init datajs
        datajs = "var data = ["
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
                    list_vl.append(str(vl))
                if field == "ModelChoiceField":
                    list_vl.append(str(vl))

            datajs += str(list_vl) + ","

        # write empty row
        for i in range(self.empty_row):
            datajs += str(["" for x in range(len(self.header))]) + ","

        # close datajs
        datajs += "];"
        jsfile = self.jspath + "/data.js"
        with open(jsfile, "w") as fl:
            fl.write(datajs)

    def populate_log(self):
        datalog = {}
        for key in self.form_class.base_fields.keys():
            datalog[key] = ""

        with open(self.filelog, "w") as fl:
            fl.write(json.dumps(datalog))
