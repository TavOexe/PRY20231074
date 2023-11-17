from decimal import Decimal
class ModelControlXoutput():
    @classmethod
    def agregar_producto_calidad_precio_orden(cls, db, orden_id, producto_id, quality_id, cantidad, kgprice, format, unity):
        try:
            cursor = db.cursor()

            # Verificar si existe stock del producto en la tabla stock_control
            cursor.execute("SELECT quantity FROM Stock_Control WHERE Product_id = '{}' AND Quality_Id = '{}'".format(producto_id, quality_id))
            existing_record = cursor.fetchone()
            #(Decimal('446.00'),)
            print(orden_id)
            #obtener el valor de la tupla
            existing_record = existing_record[0]
            # Si existe stock del producto en la tabla stock_control
            if existing_record is not None:
               #pasar cantidad a decimal
              
               cantidad = Decimal(cantidad)
                # Si la cantidad de producto a agregar es menor o igual a la cantidad de producto en stock
               if cantidad <= existing_record:
                    # Multiplica la cantidad de producto por el precio por kilo del producto
                    total_product_price = Decimal(cantidad) * Decimal(kgprice)

                    # Si la cantidad de producto a agregar es menor o igual a la cantidad de producto en stock,
                    # actualiza la cantidad de producto en stock e inserta el producto en la orden
                    new_quantity = existing_record - cantidad
                    cursor.execute("UPDATE Stock_Control SET quantity = '{}' WHERE product_id = '{}' AND Quality_Id = '{}'".format(new_quantity, producto_id, quality_id))

                    cursor.execute("INSERT INTO controlXoutput (exit_order_Id, StockControl_Product_Id, StockControl_Quality_Id, quantity, kgprice, format, unity, total_product_price) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(orden_id, producto_id, quality_id, cantidad, kgprice, format, unity, total_product_price))
                    db.commit()
               else:
                    print("No hay stock suficiente")
            else:
                print("No hay stock")

            cursor.close()
        except Exception as e:
            print(f"Error al agregar producto a la orden carajo: {e}")
            db.rollback()
            cursor.close()
