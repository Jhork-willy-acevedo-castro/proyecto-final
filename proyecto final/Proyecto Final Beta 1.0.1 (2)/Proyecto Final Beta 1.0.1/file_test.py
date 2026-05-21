import unittest
import auth
import os
import json

class AuthTest(unittest.TestCase):

    def test_registro_exitoso(self):
    
        res = auth.registerUser("nicolas", "123", "admin")
        self.assertEqual(res, "ok")
        
    
        with open(self.filename, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data["users"]), 1)
            self.assertEqual(data["users"][0]["user"], "nicolas")

    def test_usuario_duplicado(self):
        auth.registerUser("nicolas", "123", "admin")
        
        res = auth.registerUser("nicolas", "456", "viewer")
        self.assertEqual(res, "user exists")

    def test_rol_invalido(self):
        res = auth.registerUser("Arbelaez", "123", "Ingeniero")
        self.assertEqual(res, "invalid data")

if __name__ == "__main__":
    unittest.main()