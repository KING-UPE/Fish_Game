import unreal

dt = unreal.load_object(None, "/Game/Blue/Data/DT_Buildables.DT_Buildables")
if dt:
    row_names = unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)
    print("Buildables rows:", len(row_names))
    for r in row_names:
        print("Row:", r)
