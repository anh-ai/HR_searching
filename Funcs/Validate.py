from Funcs import GlobalVars as GVa


def fnValidate_Keys_in_DBCols(mdict: dict = None):
    ret = False
    mkeys = mdict.keys()
    for mkey in mkeys:
        if mkey not in GVa.List_Columns_Name:
            ret = False
    return ret
