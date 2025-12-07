from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

# --- has many Missions ---
class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Plural
    missions = db.relationship("Mission", back_populates="planet")

    # Add serialization rules
    serialize_rules = ("-missions.planet",)

# --- has many Missions ---
class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    # Plural
    missions = db.relationship("Mission", back_populates="scientist", cascade="all, delete-orphan")

    # Add serialization rules
    serialize_rules = ("-missions.scientist",)

    # Add validation
    @validates("name", "field_of_study")
    def validate_scientist_fields(self, key, value):
        """Validate that name and field_of_study are not empty."""
        if value is None or str(value).strip() == "":
            raise ValueError("Scientist must have name and field_of_study.")
        return value
    
# --- belongs to Planet and Scientist ---
class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey("scientists.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=False)

    # Singular
    planet = db.relationship("Planet", back_populates="missions")

    # Singular
    scientist = db.relationship("Scientist", back_populates="missions")

    # Add serialization rules
    serialize_rules = ("-planet.missions", "-scientist.missions")

    # Add validation
    @validates("name")
    def validate_name(self, key, value):
        """Validate that mission name is not empty."""
        if value is None or str(value).strip() == "":
            raise ValueError("Mission must have a name.")
        return value

    @validates("scientist_id", "planet_id")
    def validate_foreign_keys(self, key, value):
        """Validate that foreign keys are present."""
        if value is None:
            raise ValueError("Mission must have scientist_id and planet_id.")
        return value

# add any models you may need.
