class PurchaseOrder():
    def __init__(self, id , entrydate,format,totalquantity,comments,quantitylost,account_id,state,supplier_id)->None:
        self.id = id
        self.entrydate = entrydate
        self.format = format
        self.totalquantity = totalquantity
        self.comments = comments
        self.quantitylost = quantitylost
        self.account_id = account_id
        self.state = state
        self.supplier_id = supplier_id