import latex


def toLatexAndPdf(data, tablename):
    content = data.to_latex()
    header = "\documentclass[12pt]{article}\n\\usepackage{booktabs}\n\\begin{document}\n"
    footer = "\end{document}"
    tabledoc = header + content + footer
    with open(tablename+'.tex','w') as tablefile:
        tablefile.write(tabledoc)
    pdf = latex.build_pdf(tabledoc)
    pdf.save_to(tablename+'.pdf')
