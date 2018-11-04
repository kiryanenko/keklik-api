class XslStyles(object):
    def __init__(self, workbook):
        self.workbook = workbook

        self.title = workbook.add_format({'font_size': 30, 'bold': True})
        self.bold = workbook.add_format({'bold': True})

        self.bg_gray = workbook.add_format({'bg_color': 'gray'})
        self.bg_green = workbook.add_format({'bg_color': 'green'})
        self.bg_red = workbook.add_format({'bg_color': 'red'})
