from CustomPackages import DatabaseInteraction

wdict={}
wdict["PDF Name"] = "PDFTEST"
wdict["Name"] = "DARK COmpany"
wdict["Document No"] = "M2847124///srwr32@"
wdict["Grand total"] = "220000"
wdict["Doc date"]="23124"
wdict["Display and Mounting"] = "21424"
wdict["GST"] = "214124"
wdict["Service Tax"] = "2324"
wdict["Krishi Kalyan Cess"] = "14124"
wdict["Swatch Bharat Cess"] = "4124"
wdict["Other Charges"] = "241243"
wdict["Irn Number"] = "fyguhijo1gtyvb1j978yfbuj8y7sgtfbhutvgbji87ygho878ygh88788oij9ij"


DatabaseInteraction.commitToDB(wdict)
