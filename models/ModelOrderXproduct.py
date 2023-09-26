class ModelOrderXproduct():
    @classmethod    
    def agregar_producto_a_orden(self,db,orden_id, producto_id, cantidad):
        try:
            cursor = db.cursor()

            # Verificar si ya existe un registro para el mismo producto en la misma orden
            #cursor.execute("SELECT amount FROM orderXproducts WHERE purchase_order_Id = ? AND or_Product_Id = ?", (orden_id, producto_id))
            #existing_record = cursor.fetchone()

            # Si no existe, inserta un nuevo registro
            cursor.execute("INSERT INTO orderXproducts (purchase_order_Id, or_Product_Id, amount) VALUES (?, ?, ?)", (orden_id, producto_id, cantidad))

            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al agregar producto a la orden: {e}")
            db.rollback()
            cursor.close()