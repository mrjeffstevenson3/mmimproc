import sys, datetime


def progressbar(done, total, start=None):
    amtDone = done/float(total)
    template = "\r [{0:50s}] {1:.2f}%"
    duration = None
    if start is not None:
        duration = datetime.datetime.now() - start
        microseconds = datetime.timedelta(microseconds=duration.microseconds)
        duration = duration - microseconds
        template += "  {2}"
    msg = template.format('=' * int(amtDone * 50), amtDone * 100, duration)
    sys.stdout.write(msg)
    sys.stdout.flush()
