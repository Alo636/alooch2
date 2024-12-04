import xlsxwriter

cuaderno = xlsxwriter.Workbook("miarchivo.xlsx")

worksheet = cuaderno.add_worksheet()

nombre = "Alfredo"
dia = "24/12/2024"
hora = "7pm"

worksheet.write("A1", "Name")
worksheet.write("B1", "Day")
worksheet.write("C1", "Hour")

worksheet.write("A2", nombre)
worksheet.write("B2", dia)
worksheet.write("C2", hora)

cuaderno.close()
