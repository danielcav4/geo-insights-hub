import arcpy

# Input shapefile
input_shapefile = r"D:\ERM Projects\Active\0704216 - Cameron Downs Energy Park\Data\MSES_Clipped\Project Area 20241119\Vegetation_management_regional_ecosystem_map_V13"

# Output table
output_table = r"C:\Temp Process\RE_table_6.dbf"

# Check if the output table exists and delete it
if arcpy.Exists(output_table):
    arcpy.Delete_management(output_table)

# Dictionary to store summed areas for unique RE_Code and Category combinations
area_by_re_category = {}

# Update cursor to calculate areas for each RE code and its category
with arcpy.da.SearchCursor(input_shapefile, ["SHAPE@AREA", "RE1", "RE2", "RE3", "RE4", "RE5", "PC1", "PC2", "PC3", "PC4", "PC5", "VM_STATUS"]) as cursor:
    for row in cursor:
        total_area = row[0] / 10000  # Convert total area to hectares
        vm_status = row[11]  # VM_STATUS field
        for i in range(5):  # Iterate through RE and PC fields (RE1-RE5, PC1-PC5)
            re_code = row[i + 1]  # RE field (RE1, RE2, etc.)
            pc_value = row[i + 6]  # PC field (PC1, PC2, etc.)
            if re_code and pc_value > 0:  # Ensure valid RE code and non-zero percentage
                # Dynamically determine the category based on VM_STATUS
                if "rem" in vm_status.lower():
                    category = "Remnant"
                elif "hvr" in vm_status.lower():
                    category = "Regrowth"
                elif "non" in vm_status.lower():
                    category = "Non-remnant"
                elif "water" in vm_status.lower():
                    category = "Water"
                else:
                    category = "Unknown"

                # Calculate the area
                area = (pc_value / 100) * total_area  # Calculate area in hectares

                # Combine RE_Code and Category as a unique key for summation
                key = (re_code, category)
                if key not in area_by_re_category:
                    area_by_re_category[key] = 0
                area_by_re_category[key] += area  # Accumulate the area

# Create the output table
arcpy.CreateTable_management(out_path=r"C:\Temp Process", out_name="RE_table_6.dbf")
arcpy.AddField_management(output_table, "RE_Code", "TEXT")
arcpy.AddField_management(output_table, "Category", "TEXT")
arcpy.AddField_management(output_table, "Area_Ha", "DOUBLE")

# Insert data into the output table
with arcpy.da.InsertCursor(output_table, ["RE_Code", "Category", "Area_Ha"]) as cursor:
    for (re_code, category), total_area in area_by_re_category.items():
        cursor.insertRow([re_code, category, total_area])

print("Processing complete. The output table is saved at:", output_table)



