# -*- coding: utf-8 -*-
"""
This module contains functionality for quality control and assessment

ToDo:
"""
import os

import pandas as pd

def compare_df(df1:pd.DataFrame, df2:pd.DataFrame, output_folder) -> None:
    """
    Procedure that creates ... 
    """
    #===========================================================================
    # if ignore_sorting:
    #     df1:pd.DataFrame = df1.sort_values(unique_column)
    #     df2:pd.DataFrame = df2.sort_values(unique_column)
    #===========================================================================
    
    output_file = os.path.join(output_folder, "df_compare.txt")
    
    with open(output_file, "w") as out:
        
        out.write("Differences between compared dataframes:\n\n")
    
        df1_cols:list[object] = list(df1.columns)
        df2_cols:list[object] = list(df2.columns)
        
        out.write("Differences in number of columns:\n")
        if len(df1_cols) != len(df2_cols):
            out.write("Column number df1: {}\n".format(len(df1_cols)))
            out.write("Column number df2: {}\n\n".format(len(df2_cols)))
        else:
            out.write("None\n\n")
        
        out.write("Differences in column names:\n")
        for df1_col, df2_col in zip(df1_cols, df2_cols):
            if df1_col != df2_col:
                out.write("    ")
                out.write("{} | {}".format(df1_col, df2_col))
        
        out.write("\n\n")
        out.write("Differences in number of rows:\n")
        if len(df1) != len(df2):
            out.write("Row number df1: {}\n".format(len(df1)))
            out.write("Row number df2: {}\n\n".format(len(df2)))
        else:
            out.write("None\n\n")
        
        out.write("Value Differences:\n\n")
        
        for i in range(len(df1)):
            df1_row = df1.iloc[i]
            df2_row = df2.iloc[i]
            
            for df1_col, df2_col in zip(df1_cols, df2_cols):
                if df1_row[df1_col] != df2_row[df2_col]:
                    out.write("    ")
                    out.write("{}/{}: {}|{}".format(df1_col, df2_col, df1_row[df1_col], df2_row[df2_col]))
                    
            out.write("\n")
                
    