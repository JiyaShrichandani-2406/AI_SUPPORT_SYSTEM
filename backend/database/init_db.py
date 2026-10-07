from database.database import Base, engine
from database.models import SupportTicket, AITriageResult


print("Creating database...")

Base.metadata.create_all(bind=engine)

print("Database and tables created successfully!")