import jwt
import json
import re
import os
from pathlib import Path

def jwtdecode(encodeddata,jsonfilen,filepath):
    #encoded = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjExNUY0NDI2NjE3QTc5MzhCRTFCQTA2REJFRTkxQTQyNzU4NEVEQUIiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJFVjlFSm1GNmVUaS1HNkJ0dnVrYVFuV0U3YXMifQ.eyJkYXRhIjoie1wiU2VsbGVyR3N0aW5cIjpcIjA2QUFBQ0k2NjU3RzFaSlwiLFwiQnV5ZXJHc3RpblwiOlwiMDdBQUFDVDA4MzVEMVpTXCIsXCJEb2NOb1wiOlwiSUFIUjIwMjFETjAxMTlcIixcIkRvY1R5cFwiOlwiSU5WXCIsXCJEb2NEdFwiOlwiMDUvMDYvMjAyMFwiLFwiVG90SW52VmFsXCI6MTE4MDAwMC4wLFwiSXRlbUNudFwiOjEsXCJNYWluSHNuQ29kZVwiOlwiOTk4MzY1XCIsXCJJcm5cIjpcIjhhMWQ1ZDdkMTQ2ZGNlYTljMDdlZDRkNmEwM2M3NWNiMDk0MGNmOGIzNmRjZGJiZTQxYzU1NWI5ZjUwMTJkMDhcIn0iLCJpc3MiOiJOSUMifQ.CYk7TyKNmxvgh8sgvnUU7kB5e2W7cayjzHrP3PNm_p3js_8NqninXDmh_TqY-PBfMPx7sQwkcy0tuEJ7xHx9sgABZ8O0NUFqQYkXLHj9HtkOy91dXB8g1BmwCfPI30Y03TPauy0R2e_gqusLvC_Ls_9WqcPusD4VVFopd-_XneNeRPXDdlWuCKSKuoPJgy0l02ulJz3MlW9TZM3sYy1Few97oWt9Z5alpbb-DLu4QbZU4SB2Qpm0p8VTPcQXuaLOriwBGuxzzqOO99TgNIOIkwGP_B6EwSKds3rAd5B6uuMvMa21EpEvkVkBxVt4LNmAT5ScZrXdJp_GOmnayVoZgA'
    secret = b'''-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnzyis1ZjfNB0bBgKFMSv
    vkTtwlvBsaJq7S5wA+kzeVOVpVWwkWdVha4s38XM/pa/yr47av7+z3VTmvDRyAHc
    aT92whREFpLv9cj5lTeJSibyr/Mrm/YtjCZVWgaOYIhwrXwKLqPr/11inWsAkfIy
    tvHWTxZYEcXLgAXFuUuaS3uF9gEiNQwzGTU1v0FqkqTBr4B8nW3HCN47XUu0t8Y0
    e+lf4s4OxQawWD79J9/5d3Ry0vbV3Am1FtGJiJvOwRsIfVChDpYStTcHTCMqtvWb
    V6L11BWkpzGXSW4Hv43qa+GSYOD2QU68Mb59oSk2OB+BtOLpJofmbGEGgvmwyCI9
    MwIDAQAB
    -----END PUBLIC KEY-----'''
    f = open(jsonfilen) 
    data = json.load(f)

    outputdict = {}
    x = jwt.decode(encodeddata,secret,verify=False)

    datay = x.get("data")
    jsondata = json.loads(datay)
    
    for x in data['invoices']:
        if re.compile(x['name']).search(Path(filepath).stem):
            if 'qrdata' in x:
                for y in x['qrdata']:
                    if y:
                        outputdict[y["visualname"]] = jsondata[y["qrname"]]
        
    if outputdict:
        return outputdict
    else:
        return {}