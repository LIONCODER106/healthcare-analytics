"""
Database models and connection management
Supports MySQL, PostgreSQL, and SQLite
"""
import os
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

# Get database URL from config
try:
    DATABASE_URL = Config.get_database_url()
    print(f"✅ Database configured: {Config.DATABASE_TYPE}")
except Exception as e:
    print(f"❌ Database configuration error: {e}")
    print("Falling back to SQLite for development...")
    DATABASE_URL = "sqlite:///healthcare_fallback.db"

# Create engine with appropriate settings
engine_kwargs = {
    'pool_pre_ping': True,  # Verify connections before using
    'pool_recycle': 3600,   # Recycle connections after 1 hour
}

# Add MySQL-specific settings
if 'mysql' in DATABASE_URL:
    engine_kwargs['pool_size'] = 10
    engine_kwargs['max_overflow'] = 20
    engine_kwargs['connect_args'] = {
        'charset': 'utf8mb4',
        'connect_timeout': 10
    }
    
# Add PostgreSQL-specific settings
elif 'postgresql' in DATABASE_URL:
    engine_kwargs['pool_size'] = 10
    engine_kwargs['max_overflow'] = 20

# Create engine
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ServiceType(Base):
    """Service type definitions (medical/non-medical)"""
    __tablename__ = 'service_types'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    is_medical = Column(Boolean, default=False)
    default_rate = Column(Float, default=0.0)
    billing_method = Column(String(50), default='hourly')  # 'hourly' or 'unit'
    unit_type = Column(String(50), default='hour')  # 'hour' or '15min'
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    client_configs = relationship("ClientServiceConfig", back_populates="service_type", cascade="all, delete-orphan")


class Client(Base):
    """Client information"""
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    service_configs = relationship("ClientServiceConfig", back_populates="client", cascade="all, delete-orphan")
    period_overrides = relationship("PeriodOverride", back_populates="client", cascade="all, delete-orphan")


class ClientServiceConfig(Base):
    """Configuration of services for each client"""
    __tablename__ = 'client_service_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    service_type_id = Column(Integer, ForeignKey('service_types.id', ondelete='CASCADE'), nullable=False)
    default_hours = Column(Float, default=0.0)
    custom_rate = Column(Float, nullable=True)
    billing_method = Column(String(50), default='hourly')
    unit_type = Column(String(50), default='hour')
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    client = relationship("Client", back_populates="service_configs")
    service_type = relationship("ServiceType", back_populates="client_configs")


class PeriodOverride(Base):
    """Temporary adjustments for client services"""
    __tablename__ = 'period_overrides'
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    service_type_id = Column(Integer, ForeignKey('service_types.id', ondelete='CASCADE'), nullable=False)
    override_hours = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="period_overrides")


class ConfigHistory(Base):
    """Audit trail for configuration changes"""
    __tablename__ = 'config_history'
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(100), nullable=False)  # 'service_type', 'client', etc.
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # 'create', 'update', 'delete'
    changes = Column(Text, nullable=True)  # JSON string of changes
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="config_changes")


class ManualEntry(Base):
    """Manual entries for paper-based records"""
    __tablename__ = 'manual_entries'
    
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(255), nullable=False, index=True)
    caregiver_name = Column(String(255), nullable=False)
    service_date = Column(DateTime, nullable=False)
    service_type = Column(String(255), nullable=False)
    hours = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    entry_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="manual_entries")


class User(Base):
    """User accounts with authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    config_changes = relationship("ConfigHistory", back_populates="user")
    manual_entries = relationship("ManualEntry", back_populates="user")
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


def init_db():
    """Initialize database tables and create default data"""
    try:
        print("🔧 Initializing database...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        # Create session
        db = SessionLocal()
        
        try:
            # Check if default user exists
            existing_user = db.query(User).filter_by(username='Billingpro').first()
            if not existing_user:
                print("👤 Creating default user...")
                default_user = User(
                    username='Billingpro',
                    email='admin@healthcare.local',
                    full_name='Billing Administrator',
                    is_active=True,
                    is_admin=True
                )
                default_user.set_password('Guard2026!')
                db.add(default_user)
                db.commit()
                print("✅ Default user created (Username: Billingpro, Password: Guard2026!)")
            
            # Check if default service types exist
            existing_services = db.query(ServiceType).count()
            if existing_services == 0:
                print("🏥 Creating default service types...")
                default_services = [
                    ServiceType(
                        name='Home Health - Nursing',
                        is_medical=True,
                        default_rate=130.0,
                        billing_method='hourly',
                        description='Professional nursing services'
                    ),
                    ServiceType(
                        name='Home Health - Basic',
                        is_medical=True,
                        default_rate=41.45,
                        billing_method='hourly',
                        description='Basic home health services'
                    ),
                    ServiceType(
                        name='Home Health - Physical Therapy',
                        is_medical=True,
                        default_rate=143.0,
                        billing_method='hourly',
                        description='Physical therapy services'
                    ),
                    ServiceType(
                        name='Personal Care',
                        is_medical=False,
                        default_rate=35.0,
                        billing_method='hourly',
                        description='Non-medical personal care'
                    )
                ]
                db.add_all(default_services)
                db.commit()
                print("✅ Default service types created")
            
            print("✅ Database initialization complete!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error during data initialization: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
def close_db(db=None):
    """Close database session"""
    if db is not None:
        db.close()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

if __name__ == "__main__":
    # Test configuration and connection
    Config.print_config_info()
    print("\nTesting database connection...")
    test_connection()
