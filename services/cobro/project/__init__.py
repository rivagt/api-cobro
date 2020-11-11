import os
# from datetime import datetime
# from dateutil import parser as datetime_parser
# from dateutil.tz import tzutc
from flask import Flask, url_for, jsonify, request
from flask_cors import CORS  # , cross_origin # flask permisos
from flask_sqlalchemy import SQLAlchemy
from .utils import split_url


# basedir = os.path.abspath(os.path.dirname(__file__))
# db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)


CORS(app, resources={r"/propietarios/*": {"origins": "*"}})  # flask permisos

db = SQLAlchemy(app)


class ValidationError(ValueError):
    pass


class Propietario(db.Model):
    __tablename__ = 'propietarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True)
    dni = db.Column(db.Integer)
    propietariopropiedades = db.relationship('Propietariopropiedad',
                                             backref='propietario',
                                             lazy='dynamic')

    def get_url(self):
        return url_for('get_propietario', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'id': self.id,
            'nombres': self.nombre,
            'dni': self.dni,
            'propietariopropiedades_url': url_for('get_propietario_propiedad',
                                                  id=self.id, _external=True)
        }

    def import_data(self, data):
        try:
            self.nombre = data['nombre']
            self.dni = int(data['dni'])
        except KeyError as e:
            raise ValidationError('Invalid propietario: missing ' + e.args[0])
        return self


class Propiedad(db.Model):
    __tablename__ = 'propiedades'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    particion = db.Column(db.String(10), index=True)
    estado = db.Column(db.Integer)
    propietariopropiedades = db.relationship('Propietariopropiedad',
                                             backref='propiedad',
                                             lazy='dynamic')

    def get_url(self):
        return url_for('get_propiedad', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'numero': self.numero,
            'particion': self.particion,
            'estado': self.estado
        }

    def import_data(self, data):
        try:
            self.numero = int(data['numero'])
            self.particion = data['particion']
            self.estado = int(data['estado'])
        except KeyError as e:
            raise ValidationError('Invalid propiedad: missing ' + e.args[0])
        return self


class Cochera(db.Model):
    __tablename__ = 'cocheras'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    particion = db.Column(db.String(10), index=True)
    estado = db.Column(db.Integer)
    ppcocheras = db.relationship('Ppcochera',
                                 backref='cochera',
                                 lazy='dynamic')

    def get_url(self):
        return url_for('get_cochera', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'numero': self.numero,
            'particion': self.particion,
            'estado': self.estado
        }

    def import_data(self, data):
        try:
            self.numero = int(data['numero'])
            self.particion = data['particion']
            self.estado = int(data['estado'])
        except KeyError as e:
            raise ValidationError('Invalid propiedad: missing ' + e.args[0])
        return self


class Propietariopropiedad(db.Model):
    __tablename__ = 'propietariopropiedades'
    id = db.Column(db.Integer, primary_key=True)
    totalp = db.Column(db.Integer)
    propietario_id = db.Column(db.Integer,
                               db.ForeignKey('propietarios.id'),
                               index=True)
    propiedad_id = db.Column(db.Integer,
                             db.ForeignKey('propiedades.id'),
                             index=True)
    ppcocheras = db.relationship('Ppcochera',
                                 backref='propietariopropiedad',
                                 lazy='dynamic')
    # quantity = db.Column(db.Integer)

    def get_url(self):
        return url_for('get_propietario_propiedad', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'totalp': self.totalp,
            'propiedad_url': self.propiedad.get_url(),
            'propietario_url': self.propietario.get_url(),
            'ppcocheras_url': url_for('get_cochera_pps',
                                      id=self.id,
                                      _external=True)
            # 'quantity': self.quantity
        }

    def import_data(self, data):
        try:
            endpoint, args = split_url(data['propiedad_url'])
            self.totalp = int(data['totalp'])
        except KeyError as e:
            raise ValidationError('Invalid propietario: missing ' + e.args[0])
        if endpoint != 'get_propiedad' or 'id' not in args:
            raise ValidationError('Invalid propiedad URL: ' +
                                  data['propiedad_url'])
        self.propiedad = Propiedad.query.get(args['id'])
        if self.propiedad is None:
            raise ValidationError('Invalid propiedad URL: ' +
                                  data['propiedad_url'])
        return self


class Ppcochera(db.Model):
    __tablename__ = 'ppcocheras'
    id = db.Column(db.Integer, primary_key=True)
    propietariopropiedad_id = db.Column(db.Integer,
                                        db.ForeignKey
                                        ('propietariopropiedades.id'),
                                        index=True)
    cochera_id = db.Column(db.Integer, db.ForeignKey('cocheras.id'),
                           index=True)
    # quantity = db.Column(db.Integer)

    def get_url(self):
        return url_for('get_cochera_pp', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'pp_url': self.propietariopropiedad.get_url(),
            'cochera_url': self.cochera.get_url(),
            # 'quantity': self.quantity
        }

    def import_data(self, data):
        try:
            endpoint, args = split_url(data['cochera_url'])
        except KeyError as e:
            raise ValidationError('Invalid pp: missing ' + e.args[0])
        if endpoint != 'get_cochera' or 'id' not in args:
            raise ValidationError('Invalid cochera URL: ' +
                                  data['cochera_url'])
        self.cochera = Cochera.query.get(args['id'])
        if self.cochera is None:
            raise ValidationError('Invalid cochera URL: ' +
                                  data['cochera_url'])
        return self


@app.route('/propietarioss/<string:dni>', methods=['GET'])
def get_propietarioss(dni):
    return jsonify(Propietario.query.filter_by(dni=dni).first().export_data())


@app.route('/propietariostotal/', methods=['GET'])
def get_propietariostotal():
    return jsonify({'propietarios': [propietario.export_data() for
                                     propietario in
                                     Propietario.query.all()]})


@app.route('/propietarios/', methods=['GET'])
def get_propietarios():
    return jsonify({'propietarios': [propietario.get_url() for propietario in
                                     Propietario.query.all()]})


@app.route('/propietarios/<int:id>', methods=['GET'])
def get_propietario(id):
    return jsonify(Propietario.query.get_or_404(id).export_data())


@app.route('/propietarios/', methods=['POST', 'OPTIONS'])
def new_propietario():
    propietario = Propietario()
    propietario.import_data(request.json)
    db.session.add(propietario)
    db.session.commit()
    return jsonify({}), 201, {'Location': propietario.get_url()}


@app.route('/propietarios/<int:id>', methods=['PUT'])
def edit_propietario(id):
    propietario = Propietario.query.get_or_404(id)
    propietario.import_data(request.json)
    db.session.add(propietario)
    db.session.commit()
    return jsonify({})


@app.route('/propietarios/<int:id>', methods=['DELETE'])
def delete_propietario(id):
    propietario = Propietario.query.get_or_404(id)
    db.session.delete(propietario)
    db.session.commit()
    return jsonify({})


@app.route('/pp/', methods=['GET'])
def get_propietario_propiedades():
    return jsonify({'propietariopropiedades': [Propietariopropiedad.get_url()
                                               for Propietariopropiedad in
                                               Propietariopropiedad.query.all
                                               ()]})


@app.route('/pp/<int:id>', methods=['GET'])
def get_propietario_propiedad(id):
    return jsonify(Propietariopropiedad.query.get_or_404(id).export_data())


@app.route('/propiet/<int:id>/pp/', methods=['POST'])
def new_propietario_propiedad(id):
    propietario = Propietario.query.get_or_404(id)
    propietario_propiedad = Propietariopropiedad(propietario=propietario)
    propietario_propiedad.import_data(request.json)
    db.session.add(propietario_propiedad)
    db.session.commit()
    return jsonify({}), 201, {'Location': propietario_propiedad.get_url()}


@app.route('/pp/<int:id>', methods=['PUT'])
def edit_propietario_propiedad(id):
    propietario_propiedad = Propietariopropiedad.query.get_or_404(id)
    propietario_propiedad.import_data(request.json)
    db.session.add(propietario_propiedad)
    db.session.commit()
    return jsonify({})


@app.route('/pp/<int:id>', methods=['DELETE'])
def delete_propietario_propiedad(id):
    propietario_propiedad = Propietariopropiedad.query.get_or_404(id)
    db.session.delete(propietario_propiedad)
    db.session.commit()
    return jsonify({})


@app.route('/chpp/', methods=['GET'])
def get_cochera_pps():
    return jsonify({'ppcocheras': [Ppcochera.get_url() for Ppcochera in
                                   Ppcochera.query.all()]})


@app.route('/chpp/<int:id>', methods=['GET'])
def get_cochera_pp(id):
    return jsonify(Ppcochera.query.get_or_404(id).export_data())


@app.route('/pp/<int:id>/chpp', methods=['POST'])
def new_cochera_pp(id):
    propietario_propiedad = Propietariopropiedad.query.get_or_404(id)
    ppcochera = Ppcochera(propietariopropiedad=propietario_propiedad)
    ppcochera.import_data(request.json)
    db.session.add(ppcochera)
    db.session.commit()
    return jsonify({}), 201, {'Location': ppcochera.get_url()}


@app.route('/chpp/<int:id>', methods=['PUT'])
def edit_cochera_pp(id):
    ppcochera = Ppcochera.query.get_or_404(id)
    ppcochera.import_data(request.json)
    db.session.add(ppcochera)
    db.session.commit()
    return jsonify({})


@app.route('/chpp/<int:id>', methods=['DELETE'])
def delete_cochera_pp(id):
    ppcochera = Ppcochera.query.get_or_404(id)
    db.session.delete(ppcochera)
    db.session.commit()
    return jsonify({})


@app.route('/cochera/', methods=['GET'])
def get_cocheras():
    return jsonify({'cocheras': [Cochera.get_url() for Cochera in
                                 Cochera.query.all()]})


@app.route('/cochera/<int:id>', methods=['GET'])
def get_cochera(id):
    return jsonify(Cochera.query.get_or_404(id).export_data())


@app.route('/cochera/', methods=['POST'])
def new_cochera():
    cochera = Cochera()
    cochera.import_data(request.json)
    db.session.add(cochera)
    db.session.commit()
    return jsonify({}), 201, {'Location': cochera.get_url()}


@app.route('/cochera/<int:id>', methods=['PUT'])
def edit_cochera(id):
    cochera = Cochera.query.get_or_404(id)
    cochera.import_data(request.json)
    db.session.add(cochera)
    db.session.commit()
    return jsonify({})


@app.route('/cochera/<int:id>', methods=['DELETE'])
def delete_cochera(id):
    cochera = Cochera.query.get_or_404(id)
    db.session.delete(cochera)
    db.session.commit()
    return jsonify({})


@app.route('/propiedad/', methods=['GET'])
def get_propiedades():
    return jsonify({'propiedades': [Propiedad.get_url() for Propiedad in
                                    Propiedad.query.all()]})


@app.route('/propiedad/<int:id>', methods=['GET'])
def get_propiedad(id):
    return jsonify(Propiedad.query.get_or_404(id).export_data())


@app.route('/propiedad/', methods=['POST'])
def new_propiedad():
    propiedad = Propiedad()
    propiedad.import_data(request.json)
    db.session.add(propiedad)
    db.session.commit()
    return jsonify({}), 201, {'Location': propiedad.get_url()}


@app.route('/propiedad/<int:id>', methods=['PUT'])
def edit_propiedad(id):
    propiedad = Propiedad.query.get_or_404(id)
    propiedad.import_data(request.json)
    db.session.add(propiedad)
    db.session.commit()
    return jsonify({})


@app.route('/propiedad/<int:id>', methods=['DELETE'])
def delete_propiedad(id):
    propiedad = Propiedad.query.get_or_404(id)
    db.session.delete(propiedad)
    db.session.commit()
    return jsonify({})
