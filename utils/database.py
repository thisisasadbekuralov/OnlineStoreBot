import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    # WORK WITH CATEGORIES
    def get_categories(self):       # get all categories
        categories = self.cursor.execute(
            "SELECT id, category_name FROM categories;"
        )
        return categories.fetchall()

    def add_category(self, new_category):
        try:
            self.cursor.execute(
                "INSERT INTO categories (category_name) VALUES(?);",
                (new_category,)
            )
            self.conn.commit()
            return True
        except:
            return False

    def rename_category(self, old_name, new_name):
        try:
            self.cursor.execute(
                "UPDATE categories SET category_name=? WHERE category_name=?;",
                (new_name, old_name)
            )
            self.conn.commit()
            return True
        except:
            return False

    def delete_category(self, name):
        try:
            self.cursor.execute(
                "DELETE FROM categories WHERE category_name=?;",
                (name,)
            )
            self.conn.commit()
            return True
        except:
            return False

    def check_category_exists(self, name):
        lst = self.cursor.execute(
            f"SELECT * FROM categories WHERE category_name=?",
            (name,)
        ).fetchall()
        if not lst:
            return True
        else:
            return False

    # def add_product(self, new_product):
    #     try:
    #         self.cursor.execute(
    #             "INSERT INTO products (product_name, price, image) VALUES(?, ?, ?);",
    #             (new_product,)
    #         )
    #         self.conn.commit()
    #         return True
    #     except:
    #         return False



    def check_product_exists(self, name):
        lst = self.cursor.execute(
            f"SELECT * FROM products WHERE product_title=?",
            (name,)
        ).fetchall()
        if not lst:
            return True
        else:
            return False


    def get_products(self):  # get all categories
        categories = self.cursor.execute(
            "SELECT id, product_title FROM products;"
        )
        return categories.fetchall()


    def rename_product(self, old_name, new_name):
        try:
            self.cursor.execute(
                "UPDATE products SET product_title=?, product_price=?, product_image=? WHERE product_id=?;",
                (new_name, old_name)
            )
            self.conn.commit()
            return True
        except:
            return False


    def add_product(self, title, text, image, price, phone, u_id, cat_id):
        try:
            self.cursor.execute(
                f'INSER INTO products'
                f'(product_title,product_text,product_image,product_price,product_owner_phone_number,product_owner_id'
                f'VALUES (?,?,?,?,?,?)',
                (title, text, image, price, phone, u_id, cat_id)
            )
            self.conn.commit()
            return True
        except:
            return False
