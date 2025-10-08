from auth_manager import Base, engine

print("Connecting to the database and creating tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")