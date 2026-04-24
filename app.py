from flask import Flask
from controllers.usuario_controller import usuario_bp
from database.db import iniciar_db

app = Flask(__name__)
app.secret_key = "segredo"

# inicializa banco
iniciar_db()

# registra rotas com blueprint
app.register_blueprint(usuario_bp)

if __name__ == '__main__':
    app.run(debug=True)