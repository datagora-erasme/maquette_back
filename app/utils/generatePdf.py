from os import environ
from app import infoLogger, errorLogger
from flask import render_template
from pyhtml2pdf import converter


class generatePdf(object):
    def __init__(self, layout="layout.html", nameFile="test.pdf", datas=[]):
        self.layout = layout
        self.nameFile = nameFile
        self.datas = datas
        self.path_generated_files = environ.get("PATH_GENERATED_FILES") + "pdf/"

    def createPdf(self):
        infoLogger.info("trying to generate pdf " + self.nameFile)

        try:
            html = render_template(self.layout, datas=self.datas)
            converter.convert(html, self.path_generated_file + self.nameFile)

        except Exception as error:
            print("Error while generating the PDF file - ", error)
            errorLogger.error({"msg": str(error)})
            return False
        return True
