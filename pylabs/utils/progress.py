import sys


def progressbar(done, total):
    amtDone = done/float(total)
    template = "\r [{0:50s}] {1:.2f}%"
    sys.stdout.write(template.format('=' * int(amtDone * 50), amtDone * 100))
    sys.stdout.flush()
