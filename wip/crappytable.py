UPRLT = "┌"
UPRRT = "┐"
LOWLT = "└"
LOWRT = "┘"
HORZ  = "─"
VERT  = "│"
HORVT = "┼"
VERTL = "├"
VERTR = "┤"
HZT   = "┬"
HZB   = "┴"
def crappytable(rows):
    column_count = max([len(row) for row in rows])
    widths = []
    for column_number in range(0, column_count):
        width = max([len(str(row[column_number])) for row in rows if len(row) > column_number and row[column_number] != None])
        widths.append(width)
    table = ""
    for row in rows:
        data = [(str(row[column_number]) if len(row) > column_number and row[column_number] != None else '') for column_number in range(0, column_count)]
        data = ["%-*s" % (widths[column_number], data[column_number]) for column_number in range(0, column_count)]
        table += VERT + VERT.join(data) + VERT + "\n"
        if row == rows[0]:
            table += VERTL + HORVT.join([HORZ * width for width in widths]) + VERTR + "\n"
    return table
