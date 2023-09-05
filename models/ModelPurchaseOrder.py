from .entities.PurchaseOrder import PurchaseOrder

class ModelPurchaseOrder():
    @classmethod
    def get_all(self,db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, entrydate,format,totalquantity,comments,quantitylost,account_id,state,supplier_id FROM PurchaseOrder")
            rows = cursor.fetchall()
            purchaseorders = []
            for row in rows:
                purchaseorder = PurchaseOrder(row[0], row[1], row[2], row[3], row[4], row[5], row[6],row[7],row[8])
                purchaseorders.append(purchaseorder)
            return purchaseorders
        except Exception as e:
            print(e)
    
    @classmethod
    def new_order(self,db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, entrydate,format,totalquantity,comments,quantitylost,account_id,state,supplier_id FROM PurchaseOrder")
            rows = cursor.fetchall()
            purchaseorders = []
            for row in rows:
                purchaseorder = PurchaseOrder(row[0], row[1], row[2], row[3], row[4], row[5], row[6],row[7],row[8])
                purchaseorders.append(purchaseorder)
            return purchaseorders
        except Exception as e:
            print(e)