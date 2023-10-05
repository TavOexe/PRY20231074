from .entities.stock_control import StockControl

class ModelStockControl():
    @classmethod
    def get_all(cls,db):
        try:
            cursor = db.cursor()
            cursor.execute("Select * from stock_control")
            rows = cursor.fetchall()
            stockcontrols = []
            for row in rows:
                stockcontrol = StockControl(row[0], row[1], row[2], row[3], row[4], row[5])
                stockcontrols.append(stockcontrol)
            return stockcontrols
        except Exception as e:
            print(e)

    @classmethod
    def post(cls, db, stockcontrol):
        try:
            if stockcontrol.product_id != '' and stockcontrol.quality_id != '' and stockcontrol.quantity != '' and stockcontrol.date != '' :  
                cursor = db.cursor()
                cursor.execute("Select * from stock_control where product_id = ? and quality_id = ?", (stockcontrol.product_id, stockcontrol.quality_id))   
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute("UPDATE stock_control SET quantity = quantity + ? WHERE product_id = ? AND quality_id = ?", (stockcontrol.quantity, stockcontrol.product_id, stockcontrol.quality_id))
                else:
                    cursor.execute("INSERT INTO stock_control (product_id, quality_id, quantity, date, unity) VALUES (?, ?, ?, ?, ?)", (stockcontrol.product_id, stockcontrol.quality_id, stockcontrol.quantity, stockcontrol.date, stockcontrol.unity))
                db.commit()
                cursor.close()
                return True
        except Exception as e:
            db.rollback()
            cursor.close()
            print(e)
            return False
