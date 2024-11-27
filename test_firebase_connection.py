# import pyrebase

# # Configuração do Firebase
# config = {
#     "apiKey": "AIzaSyCA8jXrKcj8WezvwTOt-RXok-GkpEfsguI",
#     "authDomain": "sistemamapeamentolaboratorio.firebaseapp.com",
#     "databaseURL": "https://sistemamapeamentolaboratorio-default-rtdb.firebaseio.com/",
#     "projectId": "sistemamapeamentolaboratorio",
#     "storageBucket": "sistemamapeamentolaboratorio.firebasestorage.app",
#     "messagingSenderId": "659608837270",
#     "appId": "1:659608837270:web:c8f98f42a390d49cf436b7",
# }

# # Inicializando o Firebase
# firebase = pyrebase.initialize_app(config)
# database = firebase.database()

# # Função de teste de conexão e leitura de dados
# def test_firebase_connection():
#     try:
#         # Tentando acessar o nó 'usuarios'
#         data = database.child("usuarios").get()

#         if data.val() is None:
#             print("Nenhum dado encontrado no Firebase. Banco de dados vazio.")
#         else:
#             print("Dados recebidos com sucesso do Firebase:", data.val())

#     except Exception as e:
#         print(f"Erro ao tentar acessar o Firebase: {e}")

# # Chama a função de teste
# test_firebase_connection()

import pyrebase

# Configuração do Firebase
config = {
    "apiKey": "AIzaSyCA8jXrKcj8WezvwTOt-RXok-GkpEfsguI",
    "authDomain": "sistemamapeamentolaboratorio.firebaseapp.com",
    "databaseURL": "https://sistemamapeamentolaboratorio-default-rtdb.firebaseio.com/",
    "projectId": "sistemamapeamentolaboratorio",
    "storageBucket": "sistemamapeamentolaboratorio.firebasestorage.app",
    "messagingSenderId": "659608837270",
    "appId": "1:659608837270:web:c8f98f42a390d49cf436b7",
}

# Inicializando o Firebase
firebase = pyrebase.initialize_app(config)
database = firebase.database()

# Função de teste de conexão e leitura de dados
def test_firebase_connection():
    try:
        # Tentando acessar o nó 'usuarios'
        data = database.child("usuarios").get()

        if data.val() is None:
            print("Nenhum dado encontrado no Firebase. Banco de dados vazio.")
        else:
            print("Dados recebidos com sucesso do Firebase:", data.val())

    except Exception as e:
        print(f"Erro ao tentar acessar o Firebase: {e}")

# Chama a função de teste
test_firebase_connection()
