import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ['SECRET_KEY']

db = SQLAlchemy(app)

class Restaurante(db.Model):
  __tablename__ = 'restaurantes'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nombre = db.Column(db.String(120), nullable=False)
  ciudad = db.Column(db.String(80), nullable=False)
  direccion = db.Column(db.String(200))
  telefono = db.Column(db.String(30))

  platos = db.relationship(
    'Plato',
    back_populates='restaurante',
    cascade='all, delete-orphan',
    lazy=True
  )

  def __repr__(self):
    return f'<Restaurante id={self.id} nombre={self.nombre}>'

class Plato(db.Model):
  __tablename__ = 'platos'
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(120), nullable=False)
  precio = db.Column(db.Numeric(10,2), db.CheckConstraint('precio > 0'), nullable=False)
  disponible = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
  restaurante_id = db.Column(
    db.Integer,
    db.ForeignKey('restaurantes.id', ondelete='CASCADE'),
    nullable=False
  )

  restaurante = db.relationship('Restaurante', back_populates='platos')

  def __repr__(self):
    return f'<Plato id={self.id} nombre={self.nombre}>'

@app.route('/restaurantes', methods=['GET'])
def listar_restaurantes():
  # ('', '') -> vacío como segundo parámetro para evitar error AttributeError por None.strip()
  # también puede dar KeyError si no vino, tirando un 400
  # strip() = trim() -> borra los espacio del inicio y del final
  ciudad = request.args.get('ciudad', '').strip()

  consulta = (
    db.session.query(Restaurante, func.count(Plato.id).label('cantidad'))
        .outerjoin(Plato)
        .group_by(Restaurante.id)
  )

  if ciudad:
    # ilike -> no distingue entre mayúsculas y minúsculas
    # %% -> coincidencias parciales
    consulta = consulta.filter(Restaurante.ciudad.ilike(f'%{ciudad}%'))

  restaurantes = consulta.order_by(Restaurante.nombre).all()

  # (ruta archivo plantilla, variables dentro de la plantilla)
  # ciudad -> se pasa como variable dentro de la plantilla para conservar lo que el usuario escribió después de enviar el formulario, para mostrarlos después
  return render_template('restaurantes/index.html', restaurantes=restaurantes, ciudad=ciudad)

@app.route('/restaurantes/<int:restaurante_id>', methods=['GET'])
def detalle_restaurante(restaurante_id):
  # get_or_404 -> busca por id, si no encuentra nada, llama internamente a abort(404) -> este actica @app.errorhandler(404) donde ya puede decidir qué se muestra
  restaurante = db.get_or_404(Restaurante, restaurante_id)

  # se consultan aquí los platos porque si se hace desde el HTML con restaurante.platos se dispara una consulta desde el HTML
  platos = (
    Plato.query
      .filter_by(restaurante_id=restaurante_id)
      .order_by(Plato.nombre)
      .all()
  )
  
  return render_template('restaurantes/detalle.html', restaurante=restaurante, platos=platos)

@app.route('/restaurantes/crear', methods=['GET'])
def formulario_crear_restaurante():
  return render_template('restaurantes/formulario.html')

@app.route('/restaurantes/crear', methods=['POST'])
def crear_restaurante():
  try:
    restaurante = Restaurante(
      nombre=request.form.get('nombre', '').strip(),
      ciudad=request.form.get('ciudad', '').strip(),
      direccion=request.form.get('direccion', '').strip() or None,
      telefono=request.form.get('telefono', '').strip() or None,
    )

    db.session.add(restaurante)
    db.session.commit()
    flash('Restaurante creado.', 'exito')
  except Exception:
    db.session.rollback()
    flash('No se pudo crear.', 'error')
  finally:
    db.session.close()

  return redirect(url_for('listar_restaurantes'))

@app.route('/restaurantes/<int:restaurante_id>/editar', methods=['GET', 'POST'])
def editar_restaurante(restaurante_id):
  restaurante = Restaurante.query.get_or_404(restaurante_id)

  if request.method == 'GET':
    return render_template('restaurantes/formulario.html', restaurante=restaurante)

  try:
    restaurante.nombre = request.form.get('nombre', '').strip()
    restaurante.ciudad = request.form.get('ciudad', '').strip()
    restaurante.direccion = request.form.get('direccion', '').strip() or None
    restaurante.telefono = request.form.get('telefono', '').strip() or None

    db.session.commit()
    flash('Restaurante actualizado.', 'exito')
  except Exception:
    db.session.rollback()
    flash('No se pudo actualizar.', 'error')
  finally:
    db.session.close()

  return redirect(url_for('detalle_restaurante', restaurante_id=restaurante_id))

@app.route('/restaurantes/<int:restaurante_id>/eliminar', methods=['POST'])
def eliminar_restaurante(restaurante_id):
  restaurante = Restaurante.query.get_or_404(restaurante_id)

  try:
    db.session.delete(restaurante)
    db.session.commit()
    flash('Restaurante eliminado.', 'exito')
  except Exception:
    db.session.rollback()
    flash('No se pudo eliminar.', 'error')
  finally:
    db.session.close()

  return redirect(url_for('listar_restaurantes'))

@app.route('/restaurantes/<int:restaurante_id>/platos', methods=['POST'])
def crear_plato(restaurante_id):
  db.get_or_404(Restaurante, restaurante_id)

  try:
    plato = Plato(
      nombre=request.form.get('nombre', '').strip(),
      precio=request.form.get('precio', ''),
      disponible='disponible' in request.form,
      restaurante_id=restaurante_id,
    )

    db.session.add(plato)
    db.session.commit()
    flash('Plato creado.', 'exito')
  except Exception:
    db.session.rollback()
    flash('No se pudo crear.', 'error')
  finally:
    db.session.close()
  return redirect(url_for('detalle_restaurante', restaurante_id=restaurante_id))

@app.errorhandler(404)
def no_encontrado(error):
  return render_template('errores/404.html'), 404

@app.errorhandler(500)
def error_interno(error):
  db.session.rollback()
  return render_template('errores/500.html'), 500

@app.route('/', methods=['GET'])
def inicio():
  return redirect(url_for('listar_restaurantes'))

import random

# docker compose exec web flask --app app seed
@app.cli.command('seed')
def seed():
    """Carga datos de prueba: 200 restaurantes y 1000 platos."""
    ciudades = ['La Paz', 'Cochabamba', 'Santa Cruz', 'Sucre', 'Oruro', 'Tarija', 'Potosí']
    nombres_platos = ['Silpancho', 'Pique macho', 'Sajta de pollo', 'Fricasé', 'Majadito',
                      'Chicharrón', 'Anticucho', 'Sopa de maní', 'Lechón', 'Charque']
    try:
        for i in range(1, 201):
            r = Restaurante(
                nombre=f'Restaurante {i}',
                ciudad=random.choice(ciudades),
                direccion=f'Calle {i} #{100 + i}',
                telefono=f'7{i:07d}',
            )
            r.platos = [
                Plato(
                    nombre=random.choice(nombres_platos),
                    precio=round(random.uniform(10, 100), 2),
                    disponible=random.random() > 0.2,
                )
                for _ in range(5)
            ]
            db.session.add(r)
        db.session.commit()
        print('Listo: 200 restaurantes y 1000 platos.')
    except Exception:
        db.session.rollback()
        raise
    finally:
        db.session.close()

if __name__ == '__main__':
  with app.app_context():
    db.create_all() # solo crea tablas que no existen, no crea columnas agregadas a tablas ya existentes
  app.run(host='0.0.0.0', port=5000, debug=True)
