# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 11:49:00 2019

@author: mrestrepo
"""

import pandas as pd 
import glob 

files = glob.glob( "c:/Users/mrestrepo/Downloads/205-554081-73_*.xls" ) 

print( "%d files found" % len(files) )

dfs = [  pd.read_csv( file,  encoding="cp1252", sep="\t", parse_dates=[0])
         for file in files ]
df0 = pd.concat(dfs).rename( columns= {
                 "FECHA" : "date", 
                 "DOCUMENTO" : "doc", 
                 "OFICINA"  : "branch", 
                 "DESCRIPCIÓN" : "desc", 
                 "REFERENCIA" : "ref", 
                 "VALOR" : "amount"
                 })


df0["month"] = ( df0['date'].dt.year.astype(str) + "-" + 
                 df0['date'].dt.month.map( "{:02d}".format ) )

print( df0.groupby("month").agg({"date": "count"}) )


df0["amount"] = df0["amount"].str.replace(",", "").astype( float ) / 1000.0
df0["classification"] = "Sin clasificar."

df0 = df0.sort_values("date")

#%%

from collections import defaultdict
ID_BY_CLASSIF = defaultdict( int )

class Rule : 
    def __init__( self, func, 
                  classification="N/A", 
                  sub_classif="",
                  name=None ) :
        self.classif = classification
        self.func = func         
        self.sub_classif = sub_classif
        
        if name is not None :
            self.name = name 
        elif classification is not None : 
            self.name = classification + "_%d" % ID_BY_CLASSIF[classification]
            ID_BY_CLASSIF[classification] += 1
        else : 
            self.name = "rule_%d" % ID_BY_CLASSIF[classification]
            ID_BY_CLASSIF[classification] += 1
        
    def __and__( self, other ) : 
        return Rule( func = lambda df : self(df) & other(df),
                     classification = None, name=self.name + "__and__" +other.name ) 
        
    def classif_as( self, classification, sub_classif="" ) : 
        self.classif = classification 
        self.sub_classif = sub_classif
        return self 
        
    def __call__( self, df ) : 
        assert self.classif is not None
        return self.func( df )
        
    
def desc_startswith( a_str, classification="N/A-desc", sub_classif="N/A", name=None ) :
    return Rule( lambda df : df["desc"].str.startswith( a_str ),
                 classification,                 
                 name = name )
          
def transfer_svp_ref( ref, classification, sub_classif="" ) : 
    ref_str = str( ref )
    return Rule( lambda df : (df["desc"].str.startswith( "TRANSFERENCIA CTA SUC VIRT" )) & 
                             ( df["ref"].str.strip() == ref_str ),
                 classification=classification,
                 sub_classif=sub_classif)
#%%
df0["classification"] = ""
df0["sub_classif"] = ""

rules = [         
         desc_startswith("RETIRO CAJERO", "Bolsillo", name="retiro_cajero"),           
         desc_startswith("ABONO INTERESES", "Intereses", name="interes"),
         desc_startswith("AJUSTE DB INTERES AHORROS", "Intereses"), 
         desc_startswith("TRANSFERENCIA", "Transferencia" ), 
         desc_startswith("COMPRA EN", "Comida por fuera" ),
         desc_startswith("CONST / ADIC OPCION COLOMBIA", "Inversion", "Valores BC"),

         transfer_svp_ref(10042491869, "Comida por fuera"),         
         transfer_svp_ref(10312600931, "Transferencia", "Clara Mejía"),
         transfer_svp_ref(25951924850, "Transferencia", "Patricia"),
         
         desc_startswith( "COMPRA EN  TIENDA D1" , "Mercado" ),           
         desc_startswith( "PAGO DE NOM", "Sueldo"),         
         desc_startswith( "PAGO PSE Orientamos", "Arriendo"),
         desc_startswith( "PAGO PSE Empresas Publicas", "Servicios"),
         desc_startswith( "PAGO PSE UNE", "Servicios"),
         desc_startswith( "PAGO EDIFICIO",  "Propiedades/Impuestos" ),  
         desc_startswith( "PAGO PSE Superintendencia de", "Propiedades/Impuestos"),
         desc_startswith( "PAGO PSE MUNICIPIO", "Propiedades/Impuestos"),
                  
         ( desc_startswith("PAGO PSE ENLACE" ) & 
           Rule( lambda df : df["amount"].abs() < 100 ) ).classif_as( "Hogar" ),  
         
         ( desc_startswith("PAGO PSE ENLACE") & 
           Rule( lambda df : df["amount"].abs() > 100 ) 
           ).classif_as( "Inversiones", "Pago Pensión" ),  
                           
          ( desc_startswith( "CONSIGNACION") 
             & Rule( lambda df : (df["amount"] > 2350) &  (df["amount"] < 2500) )
           ).classif_as( "Propiedades/Impuestos", "Arriendo recibido" ),  
                   
           desc_startswith( "ABONO TC", "Pago TDC" ),  
           desc_startswith("DECARGUE E-PREPAGO", "Pago TDC"),
           desc_startswith("CARGUE E-PREPAGO", "Pago TDC"),
]


for rule in rules : 
    row_indicator = rule( df0 )
    df0.loc[row_indicator, "classification"] = rule.classif
    df0.loc[row_indicator, "sub_classif"] = rule.sub_classif
    
    print( rule.classif, "rule: ", rule.name, sum(row_indicator))

df0.to_excel( "C:/Users/mrestrepo/Downloads/cta_ahorros.xlsx", index=False)

df1 = ( df0.groupby( [ "classification", "sub_classif", "month"] )
           .agg({"amount" : "sum"})
           .unstack( level = -1)
           .fillna( 0 )
           )
df1.columns = [ tup[1] for tup in df1.columns ]

df1["Promedio"] = df1.mean( axis=1)
           
#%%
df2 = df0[df0.classification == ""][['desc', 'ref', 'amount']]