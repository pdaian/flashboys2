# QUICK AND DIRTY HACK FROM https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
import sys, csv
maxInt = sys.maxsize

decrement = False
try:
    csv.field_size_limit(maxInt)
except OverflowError:
    maxInt = int(maxInt/10)
    decrement = True
# END HACK

