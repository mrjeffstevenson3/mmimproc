import sys


def progressbar(done, total):
    amtDone = done/total
    template = "\r [{0:50s}] {1:.1f}%"
    sys.stdout.write(template.format('=' * int(amtDone * 50), amtDone * 100))
    sys.stdout.flush()
