import cx_Oracle
from CustomPackages import dbconfig as cfg
from datetime import datetime


def commitToDB(dict):
    """
    Insert a row to the billing_headers table
    :param billing_date:
    :param amount:
    :param customer_id:
    :param note:
    :return:
    """
    try:pdfname = dict["PDF Name"]
    except:
        print("DBINPUTERROR")
        pdfname = ""
    try:clientname = dict["Name"]
    except:
        print("DBINPUTERROR")
        clientname = ""
    try:docno = dict["Document No"]
    except:
        print("DBINPUTERROR")
        docno = ""
    try:grandtotal = dict["Grand Total"]
    except:
        print("DBINPUTERROR")
        grandtotal = ""
    try:docdate = dict["Doc date"]
    except:
        print("DBINPUTERROR")
        docdate = ""
    try:dispandmount = dict["Display and Mounting"]
    except:
        print("DBINPUTERROR")
        dispandmount = ""
    try:gst = dict["GST"]
    except:
        print("DBINPUTERROR")
        gst = ""
    try:servicetax = dict["Service Tax"]
    except:
        print("DBINPUTERROR")
        servicetax = ""
    try:krishkalyan = dict["Krishi Kalyan Cess"]
    except:
        print("DBINPUTERROR")
        krishkalyan = ""
    try:swatchbharat = dict["Swatch Bharat Cess"]
    except:
        print("DBINPUTERROR")
        swatchbharat = ""
    try:othercharges = dict["Other Charges"]
    except:
        print("DBINPUTERROR")
        othercharges = ""
    try:irnno = dict["Irn Number"]
    except:
        print("DBINPUTERROR")
        irnno = ""
    try:totalinval = dict["Total Invoice Value"]
    except:
        print("DBINPUTERROR")
        totalinval = ""
    try:selgstn = dict["Seller GST Number"] 
    except: 
        print("Error")
        selgstn = ""
    try:buygstn = dict["Buyer GST Number"]
    except:
        print("DBINPUTERROR")
        buygstn = ""
    try:qrdocnum = dict["QR DOC Number"]
    except:
        print("DBINPUTERROR")
        qrdocnum = ""
    try:qrdocdate = dict["QR DOC Date"]
    except:
        print("DBINPUTERROR")
        qrdocdate = ""
    
    # construct an insert statement that add a new row to the billing_headers table
    sql = ('insert into M_VENDOR_PDF_PARSING(PDFNAME, CLIENTNAME, DOCNO, GRANDTOTAL,DOCDATE,DISPLAYANDMOUNTING,GST,SERVICETAX,KRISHKALYANCESS,SWATCHBHARATCESS,OTHERCHARGES,IRNNO,TOTINVVAL,SELIGSTN,BUYGSTN,QRDOCNUM,QRDOCDATE) '
        'values(:pdfname,:clientname,:docno,:grandtotal,:docdate,:dispandmount,:gst,:servicetax,:krishkalyan,:swatchbharat,:othercharges,:irnno,:totalinval,:selgstn,:buygstn,:qrdocnum,:qrdocdate)')

    try:
        # establish a new connection
        with cx_Oracle.connect(cfg.username,
                            cfg.password,
                            cfg.dsn,
                            encoding=cfg.encoding) as connection:
            # create a cursor
            with connection.cursor() as cursor:
                # execute the insert statement
                cursor.execute(sql, [pdfname,clientname,docno,grandtotal,docdate,dispandmount,gst,servicetax,krishkalyan,swatchbharat,othercharges,irnno,totalinval,selgstn,buygstn,qrdocnum,qrdocdate])
                # commit work
                connection.commit()
    except cx_Oracle.Error as error:
        print('Error occurred:')
        print(error)


