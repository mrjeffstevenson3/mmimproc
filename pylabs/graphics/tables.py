import latex, subprocess


def toLatexAndPdf(data, tablename, tryImageMagickPNG=False):
    content = data.to_latex()
    header = "\documentclass[12pt]{article}\n"
    header += "\\usepackage[a5paper, landscape, margin=0.5in]{geometry}\n"
    header += "\\usepackage{booktabs}\n"
    header += "\\begin{document}\n"

    footer = "\end{document}"
    tabledoc = header + content + footer
    print('Creating latex file for '+tablename)
    with open(tablename+'.tex','w') as tablefile:
        tablefile.write(tabledoc)
    print('Creating pdf file for '+tablename)
    pdf = latex.build_pdf(tabledoc)
    pdf.save_to(tablename+'.pdf')

    if tryImageMagickPNG:
        print('Converting pdf to png for '+tablename)
        cmd = ("convert -density 300 -background white -alpha remove "+
               "{}.pdf -resize 25% {}.png")
        subprocess.check_call(cmd.format(tablename, tablename), shell=True)

